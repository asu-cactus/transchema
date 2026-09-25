import time
from dataclasses import dataclass, field
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import is_column_numerical, compare_lists_matching, compare_tables_matching
from validation.soft_match import compare_lists_matching_soft
from util.utils import get_test_info, execute_python, make_test_validation_script, resolve_main_folder, resolve_case_json, drop_leading_index_col_if_present
from test_scope import get_test_cases_ids
from auto_suggest_llm_util import (
    get_prompt,
    query_gpt,
    get_operation,
    get_columns,
    get_columns_join,
)
from eval_score.cot_score import cot_value_based_score
from hints.rule_hints import compute_case_rule_hints, format_rule_hints
from rag_pipeline.cot_rag import build_curated_rag
from judges import build_nl_score_interpretation

from log_util.log_util import create_logger

# import parameters as p
import re
import pandas as pd
import os
import traceback
from pathlib import Path
import shutil

main_folder = "autopipeline-benchmarks/github-pipelines"
source_space_dir = f"{main_folder}/intermediate_space"


allowed_operation_list = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "COLUMN_TRANSFORM",
    "NO_MORE_OPERATION",
]


@dataclass
class Config:
    target_data_name: str
    target_data_schema: str
    target_data_schema_with_types: str
    target_samples: str
    file_count: int
    source_data_name_list: list
    source_data_schema_list: list
    directory: str
    len_idx_target_idx: str
    target_perc: float
    is_perc: bool
    target_length: int
    source_length: int
    fd_flag: bool
    hint_source: str
    llm_client: LLMClient
    q_count: dict
    logger: any
    cost_summary: list
    token_tracker: TokenUsageTracker
    model: str
    token_limit: int
    static_hints: bool
    past_context: str = ""
    rag_hints: str = ""
    intermediate_scores: dict = field(default_factory=dict)
    data_split: str = "test"
    # Depth-0 rule-engine JOIN/GROUP_BY candidates for this case (see
    # hints/rule_hints.py), or None when --rule-hints is off. Computed once per case.
    rule_hint_candidates: dict = None


def get_python_response(operation_history, break_flag, csv_save_path, config: Config, intermediate_scores=None, nth_intermediate_step: int = 0, is_final: bool = False):
    logger = config.logger
    llm_client = config.llm_client
    past_context = getattr(config, "past_context", "")
    intermediate_scores = intermediate_scores or {}

    max_trails = 5
    error_str = ""
    script = ""
    response = ""
    confidence = None
    for _ in range(max_trails):
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=config.token_limit,
            model=config.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config.target_data_name,
            target_data_schema=config.target_data_schema,
            target_data_schema_with_types=config.target_data_schema_with_types,
            target_samples=config.target_samples,
            file_count=config.file_count,
            source_data_name_list=config.source_data_name_list,
            source_data_schema_list=config.source_data_schema_list,
            directory=config.directory,
            len_idx_target_idx=config.len_idx_target_idx,
            target_perc=config.target_perc,
            is_perc=config.is_perc,
            target_length=config.target_length,
            error_string=error_str,
            csv_save_path=csv_save_path,
            hint_source=config.hint_source,
            static_hints=config.static_hints,
            past_context=past_context,
            rag_hints=getattr(config, "rag_hints", ""),
            intermediate_scores=intermediate_scores,
            nth_intermediate_step=nth_intermediate_step,
            source_length=config.source_length,
            is_final=is_final,
            data_split=getattr(config, "data_split", "test"),
        )

        if prompt[0] == "-1":
            logger.info("Token Limit Exceeded")
            break_flag = 2
            break

        # Appended AFTER get_prompt() so the shared prompt builders stay untouched.
        prompt += format_rule_hints(getattr(config, "rule_hint_candidates", None))

        # get_python_script_{,final_}with_intermediate_materialization take no
        # rag_hints parameter, and get_prompt dispatches to them BEFORE the branches
        # that do -- so under --intermediate_materialization the retrieved block is
        # silently dropped. Re-attach it here when it is not already in the prompt.
        _rag = getattr(config, "rag_hints", "") or ""
        if _rag and _rag not in prompt:
            prompt += "\n" + _rag

        # The final script must be reproducible on any data split. Intermediates are
        # materialized from one split, and make_test_validation_script rewrites only
        # training_N.csv / target_multisource* -- never an intermediate path -- so a
        # final script that loads one mixes splits and silently corrupts the verdict.
        # Applied unconditionally, not just under --data_split training: a script that
        # depends on artifacts of the split it was written on is wrong either way.
        # Per-step (non-final) scripts are untouched; they are never re-run.
        if is_final:
            prompt = _strip_intermediate_paths(prompt)
            prompt += SELF_CONTAINED_FINAL_INSTRUCTION

        prompt += CONFIDENCE_INSTRUCTION

        res = query_gpt(
            llm_client,
            config.model,
            prompt,
            config.q_count,
            logger,
            config.cost_summary,
            config.token_tracker,
            type="Get Python Script",
        )
        trial_confidence, _ = parse_confidence(
            res[0], logger=logger, tag="get_python_response"
        )
        pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res[0])
        try:
            script = _strip_confidence_block(match.group(1)).strip()
            response = execute_python(script)
            error_str = error_str + response + "\n"
            # Keep the confidence from whichever response produced this script, so a
            # later failed retry cannot overwrite the accepted attempt's value.
            confidence = trial_confidence
            if response == "Success":
                break
        except Exception as e:
            print("".join(traceback.format_exc()))
            response = ""
            error_str = error_str + "No valid response from LLM.\n"
    else:
        print(f"Exceed {max_trails} trails, Materialization Failed")
    return script, response, break_flag, confidence


def create_intermediate_space(main_folder, len_id, target_id):
    # create source space (derive from main_folder so benchmark selector works)
    _source_space_dir = f"{main_folder}/intermediate_space"
    source_space_path = Path(f"{_source_space_dir}/length{len_id}_{target_id}")
    source_space_path.mkdir(exist_ok=True, parents=True)

    source_dir = Path(f"{main_folder}/length{len_id}_{target_id}")
    # Find all files matching the pattern "test{integer}.csv" in the source directory
    for file in source_dir.glob("*"):
        if file.is_file():  # Skip directories
            shutil.copy(file, source_space_path)
    return _source_space_dir


_REASONING_INSTRUCTION = (
    "\n- Please include a brief explanation of your reasoning for this choice."
)


# ── $CONFIDENCE$ block ────────────────────────────────────────────────────────
# Mirrors the MCTS mechanism (prompt block in prompts/mcts_simulate.py, parser in
# Langraph/nodes.py::_parse_pipeline_confidence) so the self-reported LLM confidence can
# feed the `confidence` component of score_1 the same way it does on the MCTS side.
#
# Reimplemented rather than imported: Langraph/nodes.py imports auto_suggest_llm_util,
# so importing from Langraph here would be circular. It lives beside
# _REASONING_INSTRUCTION because it is used identically -- appended to the prompt string
# AFTER get_prompt() returns -- which is what keeps auto_suggest_llm_util.get_prompt and
# prompts/code_generation_prompt.py (both shared with mcts_search.py) unchanged.
CONFIDENCE_INSTRUCTION = """

Rate your confidence that this script's output will exactly match the target table:
a single decimal number between 0.0 (not confident at all) and 1.0 (certain).

Emit it in the block below, as plain text OUTSIDE and BEFORE the ```Python fence.
Do NOT put this block inside the fenced code -- it is not Python and will not run.

**IMPORTANT: DO NOT FORGET TO INCLUDE THIS EXACT $CONFIDENCE$ ... $END_CONFIDENCE$
BLOCK — IF IT IS MISSING, THIS ATTEMPT WILL ERROR OUT.**

$CONFIDENCE$
0.0
$END_CONFIDENCE$

**REMINDER: DO NOT FORGET TO CLOSE THE "```Python" BLOCK WITH A CLOSING "```" AND DO
NOT FORGET THE $CONFIDENCE$ ... $END_CONFIDENCE$ BLOCK ABOVE — IF EITHER IS MISSING,
THIS ATTEMPT WILL ERROR OUT.**
"""

SELF_CONTAINED_FINAL_INSTRUCTION = """

IMPORTANT — do NOT read any intermediate_step*.csv file in this script.

Those intermediate tables were materialized from ONE data split. A script that loads
them is silently pinned to that split's data, so re-running it against another split
mixes the two and produces a wrong result.

If your plan relies on an intermediate result, that is fine — but REPRODUCE it inside
this script: include the code that builds it from the source tables listed above, then
continue from there. The intermediate tables shown above are reference material telling
you what each step should produce; the script must recompute them, not load them.
"""


_CONFIDENCE_RE = re.compile(r"\$CONFIDENCE\$(.*?)\$END_CONFIDENCE\$", re.DOTALL)
_CONFIDENCE_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _strip_confidence_block(script: str) -> str:
    """Remove any $CONFIDENCE$...$END_CONFIDENCE$ block from an extracted script.

    Models sometimes place the confidence block INSIDE the ```python fence rather than
    before it, especially in long prompts (materialization). The extractor takes
    everything between the fences, so the script then starts with "$CONFIDENCE$" and
    every execution dies with `invalid syntax (<string>, line 1)` -- five retries, no
    output, score 0, is_correct False. That looked like a model-quality regression but
    was purely a formatting collision, so strip it defensively rather than relying on
    the model to place the block correctly.
    """
    return _CONFIDENCE_RE.sub("", script)


def parse_confidence(response_text, logger=None, tag="parse_confidence"):
    """Parse the $CONFIDENCE$...$END_CONFIDENCE$ block from an LLM response.

    Returns (confidence, raw_text). `confidence` is a float in [0.0, 1.0], or None when
    the block is missing or holds no parseable number -- None is meaningful, not zero:
    the scorer renormalizes the component away rather than treating the attempt as
    maximally unconfident. Out-of-range values are clamped rather than discarded, since
    the model's intent (very low / very high) is still clear.
    """
    def _warn(message):
        if logger is not None:
            logger.warning(f"[{tag}] {message}")

    if not response_text:
        _warn("Empty response — no $CONFIDENCE$ block.")
        return None, ""

    match = _CONFIDENCE_RE.search(response_text)
    if not match:
        _warn("No $CONFIDENCE$ block found in LLM response.")
        return None, ""

    raw_text = match.group(1).strip()
    number = _CONFIDENCE_NUMBER_RE.search(raw_text)
    if not number:
        _warn(f"Unparseable confidence value: {raw_text!r}")
        return None, raw_text

    confidence = float(number.group(0))
    if not (0.0 <= confidence <= 1.0):
        _warn(f"Confidence {confidence} out of [0,1], clamping.")
        confidence = max(0.0, min(1.0, confidence))
    return confidence, raw_text


def _strip_intermediate_paths(prompt: str) -> str:
    """Remove the file paths of materialized intermediates, and the hint explaining how
    to read them, from a final-code-generation prompt.

    The materialization prompt discloses "'intermediate_step1' is stored in <path>" and
    then advises how to parse it. Arguing against both in a trailing instruction is
    fragile -- it gets weaker as more intermediates accumulate. Removing the path
    outright leaves nothing to copy, so the model has to recompute the table instead.
    Reference content (operator, schema, sample rows, score) is left untouched.
    """
    prompt = re.sub(
        r"'(intermediate_step\d+)' is stored in \S+?\.csv\.",
        r"'\1' was produced by the operations up to that step.",
        prompt,
    )
    prompt = re.sub(
        r"Important: when reading any intermediate table listed above[^\n]*\n?",
        "",
        prompt,
    )
    return prompt


def _build_op_history_entry(granularity, summary_str, ask_prompt, ask_response,
                             config_prompt=None, config_response=None):
    """Format an operation_history entry based on memory granularity.

    summary  -> compact extracted string (current behaviour)
    response -> full LLM responses only (no prompts)
    qa       -> full prompt + response for each step
    """
    if granularity == "summary":
        return summary_str
    lines = ["[Ask For Operator]"]
    if granularity == "qa":
        lines.append(f"  Prompt: {ask_prompt}")
    lines.append(f"  Response: {ask_response}")
    if config_response is not None:
        lines.append("[Configure]")
        if granularity == "qa":
            lines.append(f"  Prompt: {config_prompt}")
        lines.append(f"  Response: {config_response}")
    return "\n".join(lines)


def multi_step(args, length, id_, log_dir_, experiment_name, i_, past_context_str="", token_tracker=None, budget=None):
    # Initialize required variables
    case_path = f"{length}_{id_}"
    is_correct = False
    is_correct_ = False
    case_accuracy_ = 0
    score = 0
    case_accuracy = 0
    df_our_response = None
    fd_f1_val = 0.0
    col_ratio_val = 0.0
    debug_dict_val = {}
    cost_summary = []
    start_time = time.time()
    if token_tracker is None:
        token_tracker = TokenUsageTracker()
    script = ""
    op_hist_ = ""
    hint_source = args.hint_source
    len_id = length
    validate_fn = compare_tables_matching if getattr(args, "validation", "hard_match") == "autopipeline" else compare_lists_matching
    max_len_id = length
    target_id = id_
    max_target_id = id_
    target_per = args.target_per
    is_perc = args.is_perc
    anon_flag = args.anon_flag
    target_length = args.target_length
    source_length = args.source_length
    join_flag = args.join_flag
    aggregate_flag = args.aggregate_flag
    join_hints_truncate = args.join_hints_truncate
    aggregate_hints_truncate = args.aggregate_hints_truncate
    few_shot = args.few_shot

    fd_flag = args.fd_flag
    token_limit = args.token_limit
    model = args.model
    static_hints = args.static_hints
    # Benchmark selector: github | monteprep
    benchmark = getattr(args, "benchmark", "github")
    main_folder = resolve_main_folder(benchmark)
    source_space_dir = f"{main_folder}/intermediate_space"
    path_to_files = f"{main_folder}/length{length}_{id_}/"
    data_split = getattr(args, "data_split", "test")
    # Counting files starting with data_split prefix in this subfolder (root only, no subdirs)
    file_count = sum(
        1
        for file in os.listdir(path_to_files)
        if os.path.isfile(os.path.join(path_to_files, file))
        if file.startswith(data_split)
    )

    if args.intermediate_materialization:
        interm_space_dir = create_intermediate_space(main_folder, len_id, target_id)
        # create_intermediate_space copies sources in but never clears old outputs, and
        # get_all_intermediate loops range(1, nth_intermediate_step) picking up whatever
        # intermediate_stepN.csv exists. Without this, a shorter run inherits leftover
        # steps from a longer earlier run and feeds stale tables into the prompt as if
        # they were its own. (A four-month-old intermediate_step3.csv was found this way.)
        _interm_dir = Path(f"{interm_space_dir}/length{len_id}_{target_id}")
        for _stale in _interm_dir.glob("intermediate_step*.csv"):
            try:
                _stale.unlink()
            except OSError:
                pass
    # print(file_count)

    json_file_path = resolve_case_json(benchmark, file_count)

    log_dir = log_dir_

    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    logger = create_logger("AUTOSUGGEST", log_dir, len_id, target_id, max_target_id)

    q_count = {"total": 0, "in_task": 0}

    # Create configuration for LLM calls
    directory = source_space_dir if args.intermediate_materialization else main_folder

    # language = 'sql' #or 'python'

    ################## Run for each task ##################

    for task in task_list:  # Note: this is always only one task

        q_count["in_task"] = 0

        logger.info("Started Experiment for : " + str(task))

        cost_summary = []

        start_time = time.time()
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())
        len_idx_target_idx = task[6:]

        # Get the information of the target and source data

        (
            target_data_name,
            target_data_schema,
            target_data_schema_with_types,
            target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag, data_split=data_split)
        # added anon_flag and data_split to get_test_info() call

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger, cost_budget=budget if budget is not None else 0.0)

        target_file_location = (
            f"{main_folder}/length{len_idx_target_idx}/target_multisource.csv"
        )
        ground_truth_location = f"{main_folder}/length{len_idx_target_idx}/target.csv"

        # Depth-0 rule-engine candidates, computed once per case (cached in
        # hints/rule_hints.py) and reused by every prompt below.
        rule_hint_candidates = None
        if getattr(args, "rule_hints", False):
            rule_hint_candidates = compute_case_rule_hints(
                source_data_name_list,
                directory,
                len_idx_target_idx,
                logger=logger,
                top_k=getattr(args, "rule_hints_top_k", 3),
                data_split=data_split,
            )
        rule_hints_block = format_rule_hints(rule_hint_candidates)

        # Curated-pipeline RAG handle for this case; None unless --rag curated_pipeline.
        # Retrieval happens per operator step inside the loop below.
        curated_rag = build_curated_rag(
            args, directory, len_idx_target_idx, data_split=data_split, logger=logger
        )

        config = Config(
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_data_schema_with_types=target_data_schema_with_types,
            target_samples=target_samples,
            file_count=file_count,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            len_idx_target_idx=len_idx_target_idx,
            target_perc=target_per,
            is_perc=is_perc,
            target_length=target_length,
            source_length=source_length,
            fd_flag=fd_flag,
            hint_source=hint_source,
            llm_client=llm_client,
            q_count=q_count,
            logger=logger,
            cost_summary=cost_summary,
            token_tracker=token_tracker,
            model=model,
            token_limit=token_limit,
            directory=directory,
            static_hints=static_hints,
            past_context=past_context_str,
            data_split=data_split,
            rule_hint_candidates=rule_hint_candidates,
        )

        history_elements = []
        operation_history = []
        break_flag = 1
        granularity = getattr(args, "memory_granularity", "summary")
        intermediate_scores = {}  # {step: (true_combined_score, nl_score)}

        step = 0
        while break_flag:

            # Curated RAG is re-retrieved once per step against the plan built so far and
            # reused by this step's ask + configure prompts — the same cadence
            # _simulate_operator_level uses in Langraph/nodes.py.
            rag_hints_step = curated_rag.hints_for(operation_history) if curated_rag else ""
            # Also expose it on config: get_python_response reads config.rag_hints, and
            # under --intermediate_materialization it is called once per step from inside
            # this loop. Without this those per-step code-generation prompts get no RAG,
            # while the operator prompts around them do.
            if curated_rag:
                config.rag_hints = rag_hints_step

            prompt = get_prompt(
                prompt_type="get_next_operator",
                max_tokens=token_limit,
                model=model,
                allowed_operation_list=allowed_operation_list,
                operation_history=operation_history,
                target_data_name=target_data_name,
                target_data_schema=target_data_schema,
                target_samples=target_samples,
                target_data_schema_with_types=target_data_schema_with_types,
                file_count=file_count,
                source_data_name_list=source_data_name_list,
                source_data_schema_list=source_data_schema_list,
                directory=directory,
                len_idx_target_idx=len_idx_target_idx,
                target_perc=target_per,
                is_perc=is_perc,
                target_length=target_length,
                source_length=source_length,
                hint_source=hint_source,
                few_shot=few_shot,
                nth_intermediate_step=step + 1 if args.intermediate_materialization else 0,
                static_hints=static_hints,
                past_context=past_context_str,
                intermediate_scores=intermediate_scores,
                data_split=data_split,
                rag_hints=rag_hints_step,
            )
            if prompt[0] == "-1":
                logger.info("Token Limit Exceeded")
                break_flag = 2
                break
            # Both blocks here — they inform WHICH operator to pick next.
            prompt += rule_hints_block
            if granularity in ("response", "qa"):
                prompt += _REASONING_INSTRUCTION
            ask_prompt = prompt
            res = query_gpt(
                llm_client,
                model,
                prompt,
                q_count,
                logger,
                cost_summary,
                token_tracker,
                type="Ask For Operator",
            )
            ask_response = res[0]
            operation = get_operation(ask_response)
            print(operation)

            # operation = 'JOIN'

            if operation == "JOIN":
                # get join prompt
                prompt = get_prompt(
                    prompt_type="join",
                    max_tokens=token_limit,
                    model=model,
                    allowed_operation_list=allowed_operation_list,
                    operation_history=operation_history,
                    target_data_name=target_data_name,
                    target_data_schema=target_data_schema,
                    target_data_schema_with_types=target_data_schema_with_types,
                    target_samples=target_samples,
                    file_count=file_count,
                    source_data_name_list=source_data_name_list,
                    source_data_schema_list=source_data_schema_list,
                    directory=directory,
                    len_idx_target_idx=len_idx_target_idx,
                    target_perc=target_per,
                    is_perc=is_perc,
                    target_length=target_length,
                    join_flag=join_flag,
                    join_hints_truncate=join_hints_truncate,
                    hint_source=hint_source,
                    few_shot=few_shot,
                    nth_intermediate_step=(
                        step + 1 if args.intermediate_materialization else 0
                    ),
                    static_hints=static_hints,
                    past_context=past_context_str,
                    data_split=data_split,
                    rag_hints=rag_hints_step,
                )

                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                # Configuring a JOIN — only the JOIN candidates are relevant.
                prompt += format_rule_hints(rule_hint_candidates, kinds=("join",))
                if granularity in ("response", "qa"):
                    prompt += _REASONING_INSTRUCTION
                config_prompt = prompt
                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Configure Join",
                )
                config_response = res[0]
                joined_columns = get_columns_join(config_response)
                history_elements.append(joined_columns)
                operation_history.append(_build_op_history_entry(
                    granularity, operation + " : " + str(joined_columns),
                    ask_prompt, ask_response, config_prompt, config_response,
                ))

                # run llm and get join columns
                # add it to the history
                pass
            elif operation == "GROUP_BY/AGGREGATE":
                # get group by prompt
                prompt = get_prompt(
                    prompt_type="group_by_aggregate",
                    max_tokens=token_limit,
                    model=model,
                    allowed_operation_list=allowed_operation_list,
                    operation_history=operation_history,
                    target_data_name=target_data_name,
                    target_data_schema=target_data_schema,
                    target_data_schema_with_types=target_data_schema_with_types,
                    target_samples=target_samples,
                    file_count=file_count,
                    source_data_name_list=source_data_name_list,
                    source_data_schema_list=source_data_schema_list,
                    directory=directory,
                    len_idx_target_idx=len_idx_target_idx,
                    target_perc=target_per,
                    is_perc=is_perc,
                    target_length=target_length,
                    aggregate_flag=aggregate_flag,
                    aggregate_hints_truncate=aggregate_hints_truncate,
                    hint_source=hint_source,
                    few_shot=few_shot,
                    nth_intermediate_step=(
                        step + 1 if args.intermediate_materialization else 0
                    ),
                    static_hints=static_hints,
                    past_context=past_context_str,
                    data_split=data_split,
                    rag_hints=rag_hints_step,
                )
                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                # Configuring a GROUP BY — only the GROUP BY candidates are relevant.
                prompt += format_rule_hints(rule_hint_candidates, kinds=("group_by",))
                if granularity in ("response", "qa"):
                    prompt += _REASONING_INSTRUCTION
                config_prompt = prompt
                # run llm and get group by column
                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Configure Group by/Aggergate",
                )
                config_response = res[0]
                # add it to the history
                group_by_column = re.sub(r"```json\n|\n|```", "", config_response)
                history_elements.append(res)
                # Prefix with the operator, exactly as the JOIN and UNION branches do.
                # local_rag_db.step_to_abstract() bins a step by the text before ":",
                # so a bare "\"group_by\" = [...]" string binned as "other" and matched
                # nothing in the curated corpus -- which silently killed RAG retrieval for
                # this step AND every later one, since the prefix never matches again.
                operation_history.append(_build_op_history_entry(
                    granularity, operation + " : " + str(group_by_column),
                    ask_prompt, ask_response, config_prompt, config_response,
                ))
                # operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))
                pass
            elif operation == "UNION":
                prompt = get_prompt(
                    prompt_type="union",
                    max_tokens=token_limit,
                    model=model,
                    allowed_operation_list=allowed_operation_list,
                    operation_history=operation_history,
                    target_data_name=target_data_name,
                    target_data_schema=target_data_schema,
                    target_data_schema_with_types=target_data_schema_with_types,
                    target_samples=target_samples,
                    file_count=file_count,
                    source_data_name_list=source_data_name_list,
                    source_data_schema_list=source_data_schema_list,
                    directory=directory,
                    len_idx_target_idx=len_idx_target_idx,
                    target_perc=target_per,
                    is_perc=is_perc,
                    target_length=target_length,
                    hint_source=hint_source,
                    few_shot=few_shot,
                    nth_intermediate_step=(
                        step + 1 if args.intermediate_materialization else 0
                    ),
                    static_hints=static_hints,
                    past_context=past_context_str,
                    data_split=data_split,
                    rag_hints=rag_hints_step,
                )

                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                if granularity in ("response", "qa"):
                    prompt += _REASONING_INSTRUCTION
                config_prompt = prompt
                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Configure Union",
                )
                config_response = res[0]
                tables_ = get_columns(config_response)
                history_elements.append(tables_)
                operation_history.append(_build_op_history_entry(
                    granularity, operation + " : " + str(tables_),
                    ask_prompt, ask_response, config_prompt, config_response,
                ))
                pass
            elif operation == "PIVOT":
                operation_history.append(_build_op_history_entry(
                    granularity, operation, ask_prompt, ask_response,
                ))
                pass
            elif operation == "UNPIVOT":
                operation_history.append(_build_op_history_entry(
                    granularity, operation, ask_prompt, ask_response,
                ))
                pass
            elif operation in ("COLUMN_TRANSFORM", "COLUMN_AGGREGATION",
                               "FORMAT_DATETIME", "PROJECT"):
                # COLUMN_TRANSFORM carries no separate configure step here, the
                # same way PIVOT/UNPIVOT do not — the python-script generation reads
                # the source and target schemas to fill in the columns.
                # The pre-merge names (COLUMN_AGGREGATION / FORMAT_DATETIME /
                # PROJECT) are accepted and normalised so a model reaching for the
                # old vocabulary is not dropped.
                operation_history.append(_build_op_history_entry(
                    granularity, "COLUMN_TRANSFORM", ask_prompt, ask_response,
                ))
                pass
            elif operation == "NO_MORE_OPERATION" or operation == "" or step > 15:
                # generate python script
                # do similarity search
                # go to next
                break_flag = 0
                pass
            else:
                pass

            # Materialize the intermediate table here itself
            step += 1
            if args.intermediate_materialization and break_flag != 0:
                csv_save_path = f"{interm_space_dir}/length{len_idx_target_idx}/intermediate_step{step}.csv"
                script, response, break_flag, _ = get_python_response(
                    operation_history, break_flag, csv_save_path, config, intermediate_scores,
                    nth_intermediate_step=step,
                )
                if os.path.exists(csv_save_path):
                    try:
                        df_interm = pd.read_csv(csv_save_path, low_memory=False)
                        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
                        drop_leading_index_col_if_present(df_gt)
                        # Intermediates keep the equal-weight default: the per-length
                        # weights were calibrated against final outputs, and a partial
                        # table scored against the final target is a different quantity.
                        _, col_ratio_s, _, fd_f1_s, true_combined_s, debug_dict_s = cot_value_based_score(df_interm, df_gt)
                        nl_score_s = build_nl_score_interpretation(fd_f1_s, col_ratio_s, true_combined_s, debug_dict_s)
                        intermediate_scores[step] = (true_combined_s, nl_score_s)
                    except Exception as e:
                        logger.warning(f"Intermediate score computation failed at step {step}: {e}\n{traceback.format_exc()}")
            print(f"finished step {step}")

        # print(operation_history)

        if break_flag == 0:
            # Final retrieval against the completed plan, for the code-generation prompt.
            # get_python_response reads it off config, the same slot --rag upper_bound
            # uses in single_step_cot.
            if curated_rag:
                config.rag_hints = curated_rag.hints_for(operation_history)

            # Generate Table and Compare
            # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx)

            # put this in a loop
            script, response, break_flag, self_reported_confidence = get_python_response(
                operation_history, break_flag, target_file_location, config,
                intermediate_scores=intermediate_scores,
                nth_intermediate_step=step,
                is_final=True,
            )

            if response == "Success":
                # save file here
                # file_name
                if not os.path.exists(
                    f"{main_folder}/length{length}_{id_}/script_archive"
                ):
                    os.makedirs(f"{main_folder}/length{length}_{id_}/script_archive")
                with open(
                    f"{main_folder}/length{length}_{id_}/script_archive/{experiment_name}_{i_}.py",
                    "w",
                ) as file:
                    file.write(script)

                try:
                    # name_of_experiment_pass_1
                    df_our_response = pd.read_csv(
                        target_file_location, low_memory=False
                    )
                    df_ground_truth = pd.read_csv(
                        ground_truth_location, low_memory=False
                    )
                    df_ground_truth.drop(
                        columns=df_ground_truth.columns[0], axis=1, inplace=True
                    )
                    try:
                        (
                            case_accuracy,
                            is_correct,
                            similarity_scores,
                            shared_columns,
                        ) = validate_fn(df_our_response, df_ground_truth)
                        if (
                            is_correct == False
                            and len(shared_columns) > 0
                            and len(df_our_response) == len(df_ground_truth)
                        ):
                            print(
                                "TRY IGNORING COLUMN HEADERS AND SORTING COLUMNS FOR BETTER COMPARISON:"
                            )
                            sorted_df_our_response = df_our_response.sort_values(
                                by=shared_columns
                            )
                            sorted_df_ground_truth = df_ground_truth.sort_values(
                                by=shared_columns
                            )
                            new_header_our_response = []
                            for col in sorted_df_our_response.columns:
                                if "float" in str(sorted_df_our_response[col].dtype):
                                    print("is float")
                                    first_three_values = (
                                        sorted_df_our_response[col].head(3).astype(int)
                                    )
                                else:
                                    print("is not float")
                                    first_three_values = sorted_df_our_response[
                                        col
                                    ].head(3)
                                concatenated_header = (
                                    str(first_three_values.iloc[0])
                                    + "-"
                                    + str(first_three_values.iloc[1])
                                    + "-"
                                    + str(first_three_values.iloc[2])
                                )
                                print(concatenated_header)
                                new_header_our_response.append(concatenated_header)
                            sorted_df_our_response.columns = new_header_our_response
                            new_header_ground_truth = []
                            for col in sorted_df_ground_truth.columns:
                                if "float" in str(sorted_df_ground_truth[col].dtype):
                                    print("is float")
                                    first_three_values = (
                                        sorted_df_ground_truth[col].head(3).astype(int)
                                    )
                                else:
                                    print("is not float")
                                    first_three_values = sorted_df_ground_truth[
                                        col
                                    ].head(3)
                                concatenated_header = (
                                    str(first_three_values.iloc[0])
                                    + "-"
                                    + str(first_three_values.iloc[1])
                                    + "-"
                                    + str(first_three_values.iloc[2])
                                )
                                print(concatenated_header)
                                new_header_ground_truth.append(concatenated_header)
                            sorted_df_ground_truth.columns = new_header_ground_truth
                            print("OUR RESPONSE:")
                            print(sorted_df_our_response)
                            print("GROUND TRUTH:")
                            print(sorted_df_ground_truth)
                            (
                                case_accuracy,
                                is_correct,
                                similarity_scores,
                                shared_columns,
                            ) = validate_fn(
                                sorted_df_our_response, sorted_df_ground_truth
                            )

                        # The score is independent of the header-fallback branch above,
                        # so compute it for every attempt. It previously sat in an
                        # `else:` here, leaving score = 0 for any case that took the
                        # fallback even though the output was perfectly scoreable.
                        try:
                            _, col_ratio_val, _, fd_f1_val, score, debug_dict_val = cot_value_based_score(
                                df_our_response,
                                df_ground_truth,
                                length=length,
                                confidence=self_reported_confidence,
                            )
                        except Exception:
                            logger.warning(
                                f"Score computation failed for {length}_{id_}, leaving "
                                f"score=0:\n{traceback.format_exc()}"
                            )
                    except Exception as e:
                        print("".join(traceback.format_exc()))
                        is_correct = False
                except Exception as e:
                    print("".join(traceback.format_exc()))
                    case_accuracy = 0
                    is_correct = False
                    score = 0
        # Two-phase validation: score on training output, is_correct on test output
        if data_split == "training" and script:
            test_script = make_test_validation_script(script)
            test_output = f"{main_folder}/length{len_idx_target_idx}/target_multisource_test_val.csv"
            print("[two-phase ms] executing test-data script for is_correct validation...")
            test_exec = execute_python(test_script)
            if test_exec == "Success" and os.path.exists(test_output):
                try:
                    df_test = pd.read_csv(test_output, low_memory=False)
                    df_gt_test = pd.read_csv(ground_truth_location, low_memory=False)
                    drop_leading_index_col_if_present(df_gt_test)
                    _, test_is_correct, _, _ = validate_fn(df_test, df_gt_test)
                    print(f"[two-phase ms] is_correct: training={is_correct} → test={test_is_correct}")
                    is_correct = test_is_correct
                except Exception:
                    print(f"[two-phase ms] test validation failed:\n{traceback.format_exc()}")
            else:
                print(f"[two-phase ms] test exec={test_exec}, output_exists={os.path.exists(test_output)}")

        op_hist_ = str(operation_history)
    end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        recovered_path = f"{main_folder}/length{length}_{id_}/python_recovered.py"
        with open(recovered_path, "w") as file:
            file.write(script)
        print(f"[multi_step] python_recovered.py written: {recovered_path}")
    case_path = f"{length}_{id_}"
    cost_data = token_tracker.cost_summary()  # This returns a dictionary
    total_cost = cost_data.get("total_cost", 0.0)  # Safely get total_cost with default
    time_elapsed = end_time - start_time
    ms_info = (
        is_correct,
        total_cost,  # Use the extracted total_cost value
        time_elapsed,
        score,
        op_hist_,
    )
    print(f"ms_info: {ms_info}")
    logger.info("Total Queries Made : {q}".format(q=q_count["total"]))

    return ms_info, (df_our_response, fd_f1_val, col_ratio_val, score, debug_dict_val)
