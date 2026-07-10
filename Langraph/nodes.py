"""
LangGraph node functions for the MCTS schema transformation graph.

Each function takes MCTSGraphState and returns a dict of state updates.
Tree mutations (visits, children, rewards) happen in-place on MCTSNode objects
— those updates are NOT returned in the dict because the `root` reference in
the state already points to the live tree.

MCTS phases
-----------
  Selection    → mcts_select
  Expansion    → next_operator_step  (one operator added to tree per iteration)
  Simulation   → simulate            (LLM completes pipeline + generates code)
  Scoring      → execute_and_score   (calculate_score reward)
  Backprop     → backpropagate

Other nodes
-----------
  extract_best  — save best result to disk, finalize state

Conditional edge functions (return routing strings)
-----------------------------------------------------
  is_selected_terminal — after mcts_select
  check_budget         — after backpropagate
"""

import json
import multiprocessing
import os
import re
import sys
import traceback
from typing import Any, Dict, List

import pandas as pd

# ── Path setup: nodes.py lives in Langraph/, parent is the project root ──────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# eval_score/score.py uses relative imports (fdtool, column_map_utils) that
# live inside the eval_score/ directory, so add it to sys.path as well.
_EVAL_SCORE = os.path.join(_ROOT, "eval_score")
if _EVAL_SCORE not in sys.path:
    sys.path.insert(0, _EVAL_SCORE)

from judges import judge as llm_judge_fn, build_nl_score_interpretation
from rag_pipeline.local_rag_db import get_rag_hints

from auto_suggest_llm_util import (
    get_mcts_candidates,
    get_operation,
    get_columns,
    get_columns_join,
    get_prompt,
    query_gpt,
)
from eval_score.score import relative_csv_score
from eval_score_value_based import value_based_relative_csv_score, value_based_relative_csv_score_timed
from llm.llm_models import CostBudgetExceeded
from mcts_node import (
    MCTSNode,
    OPERATOR_TYPES,
    EXPAND_OPERATOR_TYPES,
    STRUCTURAL_EXPAND_OPS,
    AGGREGATE_MAX_CHILDREN,
)
from state import MCTSGraphState
from util.utils import execute_python
from validation.hard_match import compare_lists_matching, compare_tables_matching
from validation.fuzzy_match import compare_tables_fuzzy

# Maximum tree selection depth (used in mcts_select only)
_MAX_SELECT_DEPTH = 15
# Minimum reward needed on a GROUP_BY subtree to trigger reaggregation_needed
_REAGGREGATION_REWARD_THRESHOLD = 0.5
# Maximum code-generation retries inside simulate
_MAX_CODE_TRIALS = 5
# Maximum operator steps in one operator-level simulation rollout
_MAX_SIMULATE_STEPS = 15
# Hard timeout (seconds) for the full scoring + validation call
_SCORE_TIMEOUT = 60


def _score_worker(target_file_location: str, ground_truth_location: str, result_queue,
                  gt_cache_path: str = ""):
    """Subprocess worker: load CSVs and compute score, put result in queue.

    Accepts file paths instead of DataFrames to avoid pickling overhead.
    Loads pre-computed GT data from *gt_cache_path* when available so that
    FD mining and self-column-map on the (static) ground truth are skipped.
    If the cache recorded that GT was reduced (col_indices set), df_gt is
    reduced to the same columns/rows before scoring.
    """
    try:
        df_output = pd.read_csv(target_file_location, low_memory=False)
        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        precomputed_gt = None
        if gt_cache_path and os.path.exists(gt_cache_path):
            try:
                with open(gt_cache_path) as _f:
                    _cache = json.load(_f)
                col_indices = _cache.get("col_indices")
                max_fd_rows = _cache.get("max_fd_rows")
                if col_indices is not None:
                    df_gt = df_gt.iloc[:max_fd_rows, col_indices]
                precomputed_gt = {
                    "FDs_b": [(_item["lhs"], _item["rhs"]) for _item in _cache["FDs_b"]],
                    "E_b": _cache["E_b"],
                    "keys_b": _cache["keys_b"],
                    "self_col_count": _cache["self_col_count"],
                    "max_fd_rows": max_fd_rows,
                }
            except Exception:
                precomputed_gt = None

        _, _, _, _, true_combined_score, _ = relative_csv_score(
            df_output, df_gt, precomputed_gt=precomputed_gt
        )
        result_queue.put(true_combined_score)
    except Exception:
        result_queue.put(0.0)


def _score_with_timeout(target_file_location: str, ground_truth_location: str,
                        gt_cache_path: str = "") -> float:
    """Run scoring in a child process with a hard timeout.

    Passes file paths (not DataFrames) to avoid pickling overhead.
    The child process is terminate()d on timeout, which actually stops
    get_column_map / relative_csv_score — unlike threads, which cannot be
    killed when stuck in C extensions.
    Returns 0.0 on timeout or error.
    """
    q = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=_score_worker,
        args=(target_file_location, ground_truth_location, q, gt_cache_path),
        daemon=True,
    )
    p.start()
    p.join(timeout=_SCORE_TIMEOUT)
    if p.is_alive():
        p.terminate()
        p.join()
        return 0.0
    try:
        return q.get_nowait()
    except Exception:
        return 0.0


_MAX_SCORE_COLS = 20
_MAX_SCORE_ROWS = 2000


def _apply_symmetric_truncation(df_output, df_gt):
    """Truncate both tables to 20 evenly-spaced GT cols + 2000 rows each.
    Returns (df_output_truncated, df_gt_truncated, precomputed_gt=None).
    precomputed_gt is None so FDs are recomputed on the truncated GT.
    """
    if len(df_gt.columns) > _MAX_SCORE_COLS:
        df_gt = df_gt.iloc[:_MAX_SCORE_ROWS, :_MAX_SCORE_COLS]
    else:
        df_gt = df_gt.iloc[:_MAX_SCORE_ROWS]
    df_output = df_output.iloc[:_MAX_SCORE_ROWS]
    return df_output, df_gt, None  # precomputed_gt=None → recompute on truncated GT


def _value_score_worker(target_file_location: str, ground_truth_location: str, result_queue,
                        gt_cache_path: str = "", force_truncate: bool = False, weights: dict | None = None):
    """Subprocess worker: load CSVs and compute value_based score, put result in queue.

    Uses Jaccard-aligned column matching + value-based distribution scoring.
    If the cache recorded GT was reduced (col_indices set), or force_truncate=True,
    both df_gt and df_output are truncated symmetrically before scoring.

    weights: optional score_1 component weights (fd_f1/avg_col_score_1/
        row_count_score/max_missing_score), forwarded to
        value_based_relative_csv_score. Defaults to equal weights there.
    Puts a dict {"score": float, "components": {...} | None} in result_queue
    -- components are the 4 raw (unweighted) score_1 inputs, logged
    regardless of which weights produced the score, so the score can be
    recomputed under different weights later without rerunning MCTS.
    """
    try:
        df_output = pd.read_csv(target_file_location, low_memory=False)
        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        precomputed_gt = None
        col_indices = None
        max_fd_rows = None

        if gt_cache_path and os.path.exists(gt_cache_path):
            try:
                with open(gt_cache_path) as _f:
                    _cache = json.load(_f)
                col_indices = _cache.get("col_indices")
                max_fd_rows = _cache.get("max_fd_rows")
                if col_indices is not None:
                    df_gt = df_gt.iloc[:max_fd_rows, col_indices]
                    df_output = df_output.iloc[:max_fd_rows]  # symmetric row cap
                precomputed_gt = {
                    "FDs_b": [(_item["lhs"], _item["rhs"]) for _item in _cache["FDs_b"]],
                    "E_b": _cache["E_b"],
                    "keys_b": _cache["keys_b"],
                    "self_col_count": _cache["self_col_count"],
                    "max_fd_rows": max_fd_rows,
                }
            except Exception:
                precomputed_gt = None

        if force_truncate and col_indices is None:
            # Scoring timed out on the full table — truncate both symmetrically
            df_output, df_gt, precomputed_gt = _apply_symmetric_truncation(df_output, df_gt)

        _, _, _, fd_f1, true_combined_score, debug_dict = value_based_relative_csv_score(
            df_output, df_gt, precomputed_gt=precomputed_gt, weights=weights
        )
        components = {
            "fd_f1": fd_f1,
            "avg_col_score_1": debug_dict.get("avg_col_score_1"),
            "row_count_score": debug_dict.get("row_count_score"),
            "max_missing_score": debug_dict.get("max_missing_score"),
        }
        result_queue.put({"score": true_combined_score, "components": components})
    except Exception:
        result_queue.put({"score": 0.0, "components": None})


def _value_score_with_timeout(target_file_location: str, ground_truth_location: str,
                              gt_cache_path: str = "", weights: dict | None = None):
    """Run value_based scoring in a child process with a hard timeout.

    Phase 1: score on the (possibly GT-truncated) tables.
    Phase 2: if Phase 1 times out, retry with symmetric truncation of both tables
             (20 evenly-spaced GT cols + 2000 rows each) so scoring always completes.

    Returns (score, components) -- components is a dict of the 4 raw
    (unweighted) score_1 inputs, or None on timeout/error.
    """
    def _run(force_truncate: bool):
        q = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=_value_score_worker,
            args=(target_file_location, ground_truth_location, q, gt_cache_path, force_truncate, weights),
            daemon=True,
        )
        p.start()
        p.join(timeout=_SCORE_TIMEOUT)
        if p.is_alive():
            p.terminate()
            p.join()
            return None, None, True  # timed out
        try:
            result = q.get_nowait()
            return result["score"], result["components"], False
        except Exception:
            return 0.0, None, False

    score, components, timed_out = _run(force_truncate=False)
    if timed_out:
        # Phase 2: truncate both tables symmetrically and retry
        score, components, _ = _run(force_truncate=True)
        if score is None:
            score = 0.0
    return score, components


def _score_and_validate_output(
    target_file_location: str,
    ground_truth_location: str,
    validation_mode: str,
    reward_mode: str,
    gt_cache_path: str = "",
    score_weights: dict | None = None,
):
    """
    Load output + ground truth and compute only the metric required by reward_mode:
      - "score"           : relative_csv_score (FD + column map + distribution)
      - "det_score_value" : value_based_relative_csv_score (Jaccard-aligned columns + value-based distribution)
      - "validation"      : avg_similarity from compare_lists/tables_matching (per-col × per-row)
      - "partial"         : fuzzy column-match ratio from compare_tables_fuzzy

    Returns (reward, is_correct, components) where is_correct is derived from
    reward >= threshold. components is a dict of the 4 raw (unweighted)
    score_1 inputs when reward_mode="det_score_value" (None otherwise, and
    None on timeout/scoring error) -- logged regardless of score_weights so
    the score can be recomputed under different weights later.
    gt_cache_path: path to pre-computed GT JSON cache; passed to subprocess workers to
                   skip per-iteration FD mining and self-column-map on ground truth.
    score_weights: optional score_1 component weights (fd_f1/avg_col_score_1/
                   row_count_score/max_missing_score), only used when
                   reward_mode="det_score_value". Defaults to equal weights.
    """
    df_output = pd.read_csv(target_file_location, low_memory=False)
    df_gt = pd.read_csv(ground_truth_location, low_memory=False)
    df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

    _SCORE_THRESHOLD = 0.9  # default stopping threshold
    # det_score_value uses a stricter 1.0 threshold to avoid false-positive early stops
    _DET_SCORE_THRESHOLD = 1.0

    if reward_mode == "validation":
        validate_fn = (
            compare_tables_matching if validation_mode == "autopipeline" else compare_lists_matching
        )
        avg_similarity, _, _, _ = validate_fn(df_output, df_gt)
        return float(avg_similarity), float(avg_similarity) >= _SCORE_THRESHOLD, None

    elif reward_mode == "partial":
        partial, _ = compare_tables_fuzzy(df_output, df_gt)
        return float(partial), float(partial) >= _SCORE_THRESHOLD, None

    elif reward_mode == "det_score_value":
        score, components = _value_score_with_timeout(
            target_file_location, ground_truth_location, gt_cache_path, weights=score_weights
        )
        return score, score >= _DET_SCORE_THRESHOLD, components

    else:  # "score"
        score = _score_with_timeout(target_file_location, ground_truth_location, gt_cache_path)
        return score, score >= _SCORE_THRESHOLD, None


# ─────────────────────────────────────────────────────────────────────────────
# Critique helpers for path tree traversal/creation
# ─────────────────────────────────────────────────────────────────────────────


def _parse_op_type(step: str) -> str:
    """
    Extract operator type from a configured step string.
    E.g. "JOIN : [[T0, T1]] columns=..." → "JOIN"
         "GROUP_BY/AGGREGATE : ..." → "GROUP_BY/AGGREGATE"
         "GROUP_BY : [col1, col2]"  → "GROUP_BY"
         "AGGREGATE : [COUNT(col)]" → "AGGREGATE"
         "NO_MORE_OPERATION"        → "NO_MORE_OPERATION"
    """
    if step == "NO_MORE_OPERATION":
        return "NO_MORE_OPERATION"
    if step.startswith("GROUP_BY/AGGREGATE"):
        return "GROUP_BY/AGGREGATE"
    if step.startswith("GROUP_BY :"):
        return "GROUP_BY"
    if step.startswith("AGGREGATE :"):
        return "AGGREGATE"
    return step.split(":")[0].strip()


def _split_groupby_aggregate(history: List[str]) -> List[str]:
    """Reverse of _merge_groupby_aggregate.

    Splits any GROUP_BY/AGGREGATE step from simulation or critique output back
    into separate GROUP_BY and AGGREGATE steps so the tree stays consistent with
    the expand-layer structure.

    Handles two formats produced by different prompts:
      Format 1 (configure):  GROUP_BY/AGGREGATE : "group_by" = [...], "aggregations" = [...]
      Format 2 (simulate):   GROUP_BY/AGGREGATE : group_by=[...] aggregations=[...]

    Steps that cannot be parsed are passed through unchanged.
    """
    result: List[str] = []
    for step in history:
        if "GROUP_BY/AGGREGATE" not in step:
            result.append(step)
            continue

        after_colon = step.split(":", 1)[1].strip() if ":" in step else step

        # Format 1: "group_by" = [...], "aggregations" = [...]
        m_gb = re.search(r'"group_by"\s*=\s*(\[.*?\])', after_colon)
        m_agg = re.search(r'"aggregations"\s*=\s*(\[.*\])\s*$', after_colon, re.DOTALL)
        if m_gb and m_agg:
            result.append(f"GROUP_BY : {m_gb.group(1)}")
            result.append(f"AGGREGATE : {m_agg.group(1).strip()}")
            continue

        # Format 2: group_by=[...] aggregations=[...]
        m_gb2 = re.search(r'\bgroup_by=(\[.*?\])', after_colon, re.IGNORECASE)
        m_agg2 = re.search(r'\baggregations=(\[.*\])\s*$', after_colon, re.IGNORECASE | re.DOTALL)
        if m_gb2 and m_agg2:
            result.append(f"GROUP_BY : {m_gb2.group(1)}")
            result.append(f"AGGREGATE : {m_agg2.group(1).strip()}")
            continue

        result.append(step)  # unparseable — keep as-is
    return result


def _merge_groupby_aggregate(history: List[str]) -> List[str]:
    """Collapse consecutive GROUP_BY + AGGREGATE tree steps into the single
    GROUP_BY/AGGREGATE string that simulation and code-gen understand.

    "GROUP_BY : [col1]"      }
    "AGGREGATE : [COUNT(c)]" }  →  'GROUP_BY/AGGREGATE : "group_by" = [col1], "aggregations" = [COUNT(c)]'

    Any GROUP_BY not immediately followed by AGGREGATE is passed through unchanged
    (shouldn't happen in normal flow, but safe to handle).
    """
    merged: List[str] = []
    i = 0
    while i < len(history):
        step = history[i]
        if (
            step.startswith("GROUP_BY :")
            and i + 1 < len(history)
            and history[i + 1].startswith("AGGREGATE :")
        ):
            gb_cols = step[len("GROUP_BY :"):].strip()
            agg_fns = history[i + 1][len("AGGREGATE :"):].strip()
            merged.append(
                f'GROUP_BY/AGGREGATE : "group_by" = {gb_cols}, "aggregations" = {agg_fns}'
            )
            i += 2
        else:
            merged.append(step)
            i += 1
    return merged


def _find_or_create_path(root: MCTSNode, critique_history: List[str]) -> List[MCTSNode]:
    """
    Walk the tree from root, reusing existing child nodes where the step string
    matches, and creating new MCTSNode children where it doesn't. Returns the
    full path [root, ..., leaf].

    NO_MORE_OPERATION steps are stripped before walking — terminal markers from
    simulation output must never become tree nodes.
    """
    # Strip terminal markers — they are simulation artifacts, not tree structure.
    steps = [s for s in critique_history if s != "NO_MORE_OPERATION"]

    path = [root]
    node = root
    for i, step in enumerate(steps):
        child_history = steps[: i + 1]
        if step in node.children:
            node = node.children[step]
        else:
            op_type = _parse_op_type(step)
            node = node.add_child(step, child_history, operator_type=op_type)
        path.append(node)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Simulation helpers (shared by pipeline-level and operator-level simulate)
# ─────────────────────────────────────────────────────────────────────────────


def _simulate_get_python(
    operation_history: List[str],
    target_file_location: str,
    state: "MCTSGraphState",
    csv_save_path: str = None,
    nth_intermediate_step: int = 0,
    intermediate_scores: dict = None,
    is_final: bool = False,
) -> tuple:
    """
    Generate a Python script from a finalized operation_history using the
    'python_script' prompt type.  Retries up to _MAX_CODE_TRIALS times,
    feeding execution errors back into each successive prompt.

    Returns (script: str, response: str) where response is "Success" or the
    last error string.
    """
    config = state["config"]
    save_path = csv_save_path if csv_save_path is not None else target_file_location

    # Strip NO_MORE_OPERATION so the prefix length = structural ops only;
    # otherwise depth == len(abstract) and the "has next step" guard always fails.
    _rag_op_history = [op for op in operation_history if op != "NO_MORE_OPERATION"]
    rag_hints = get_rag_hints(
        state.get("local_rag_db_path", ""),
        _rag_op_history,
    )
    if rag_hints:
        config.logger.info(
            f"[simulate/python] RAG hints retrieved for history depth={len(_rag_op_history)}"
        )

    error_str = ""
    script = ""
    response = ""

    for trial in range(_MAX_CODE_TRIALS):
        try:
            prompt = get_prompt(
                prompt_type="python_script",
                max_tokens=config.token_limit,
                model=config.model,
                allowed_operation_list=OPERATOR_TYPES,
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
                source_length=config.source_length,
                error_string=error_str,
                csv_save_path=save_path,
                hint_source=config.hint_source,
                static_hints=getattr(config, "static_hints", True),
                fd_flag=int(config.fd_flag),
                nth_intermediate_step=nth_intermediate_step,
                intermediate_scores=intermediate_scores or {},
                is_final=is_final,
                data_split=getattr(config, "data_split", "test"),
                rag_hints=rag_hints,
            )
        except Exception:
            config.logger.warning(
                f"[simulate/python] get_prompt failed (trial {trial}): "
                f"{traceback.format_exc()}"
            )
            break

        res = query_gpt(
            config.llm_client,
            config.model,
            [prompt],
            config.q_count,
            config.logger,
            config.cost_summary,
            config.token_tracker,
            type="MCTS Simulate Python",
        )

        pattern = re.compile(r"```[Pp]ython(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res[0])
        if not match:
            error_str += "No valid Python code block found in LLM response.\n"
            config.logger.warning(f"[simulate/python] No code block (trial {trial})")
            continue

        script = match.group(1).strip()
        response = execute_python(script)
        error_str += response + "\n"
        config.logger.info(f"[simulate/python] trial {trial}: {response}")

        if response == "Success":
            break
    else:
        config.logger.warning(
            f"[simulate/python] Exceeded {_MAX_CODE_TRIALS} trials. "
            f"Last response: '{response}'"
        )

    return script, response


def _simulate_operator_level(state: "MCTSGraphState") -> tuple:
    """
    Operator-level simulation: mirrors the multistep process in multi_step.py.

    Starting from rollout_history (partial plan from expansion), iteratively
    asks the LLM for each next operator and configures it, building sim_history
    one step at a time until NO_MORE_OPERATION, then generates Python code.

    Returns (script: str, response: str, sim_history: List[str]).
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]
    target_file_location: str = state["target_file_location"]

    join_flag: int = state.get("join_flag", 0)
    join_hints_truncate: List[float] = state.get("join_hints_truncate", [])
    aggregate_flag: int = state.get("aggregate_flag", 0)
    aggregate_hints_truncate: List[float] = state.get("aggregate_hints_truncate", [])
    few_shot: int = state.get("few_shot", 0)

    intermediate_materialization: bool = state.get("intermediate_materialization", False)
    intermediate_scores: dict = {}
    ground_truth_location: str = state["ground_truth_location"]

    # Terminal re-simulation: rollout_history already ends with NO_MORE_OPERATION;
    # skip the operator loop and go straight to code generation.
    is_already_terminal = (
        bool(rollout_history) and rollout_history[-1] == "NO_MORE_OPERATION"
    )

    if is_already_terminal:
        sim_history = list(rollout_history)
        config.logger.info(
            f"[simulate/op] Iter {state['iteration']}: "
            f"terminal re-simulation — skipping operator loop"
        )
    else:
        sim_history = list(rollout_history)
        step = 0

        while step < _MAX_SIMULATE_STEPS:
            # ── Ask: what is the next operator? ──────────────────────────
            rag_hints_step = get_rag_hints(
                state.get("local_rag_db_path", ""),
                sim_history,
            )
            if rag_hints_step:
                config.logger.info(
                    f"[simulate/op] RAG hints retrieved at step {step} "
                    f"(prefix depth={len(sim_history)})"
                )
            try:
                next_op_prompt = get_prompt(
                    prompt_type="get_next_operator",
                    max_tokens=config.token_limit,
                    model=config.model,
                    allowed_operation_list=OPERATOR_TYPES,
                    operation_history=sim_history,
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
                    source_length=config.source_length,
                    hint_source=config.hint_source,
                    few_shot=few_shot,
                    fd_flag=int(config.fd_flag),
                    static_hints=getattr(config, "static_hints", True),
                    nth_intermediate_step=step + 1 if intermediate_materialization else 0,
                    intermediate_scores=intermediate_scores,
                    data_split=getattr(config, "data_split", "test"),
                    rag_hints=rag_hints_step,
                )
            except Exception:
                config.logger.warning(
                    f"[simulate/op] get_next_operator prompt failed (step {step}): "
                    f"{traceback.format_exc()}"
                )
                break

            op_res = query_gpt(
                config.llm_client,
                config.model,
                [next_op_prompt],
                config.q_count,
                config.logger,
                config.cost_summary,
                config.token_tracker,
                type="MCTS Sim Get Next Op",
            )
            operation = get_operation(op_res[0])
            config.logger.info(
                f"[simulate/op] step {step}: get_next_operator → '{operation}'"
            )

            # Stop operator loop on terminal / unrecognised response
            if not operation or operation in ("NO_MORE_OPERATION", "No match found"):
                sim_history.append("NO_MORE_OPERATION")
                break

            # ── Configure the chosen operator ─────────────────────────────
            configured_step: str = ""

            if operation == "JOIN":
                try:
                    if rag_hints_step:
                        config.logger.info(
                            f"[simulate/op] RAG hints retrieved for configure_join at step {step} "
                            f"(prefix depth={len(sim_history)})"
                        )
                    cfg_prompt = get_prompt(
                        prompt_type="join",
                        max_tokens=config.token_limit,
                        model=config.model,
                        allowed_operation_list=OPERATOR_TYPES,
                        operation_history=sim_history,
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
                        source_length=config.source_length,
                        join_flag=join_flag,
                        join_hints_truncate=join_hints_truncate,
                        hint_source=config.hint_source,
                        few_shot=few_shot,
                        fd_flag=int(config.fd_flag),
                        static_hints=getattr(config, "static_hints", True),
                        nth_intermediate_step=step + 1 if intermediate_materialization else 0,
                        intermediate_scores=intermediate_scores,
                        data_split=getattr(config, "data_split", "test"),
                        rag_hints=rag_hints_step,
                    )
                except Exception:
                    config.logger.warning(
                        f"[simulate/op] join prompt failed (step {step}): "
                        f"{traceback.format_exc()}"
                    )
                    step += 1
                    continue
                cfg_res = query_gpt(
                    config.llm_client, config.model, [cfg_prompt],
                    config.q_count, config.logger, config.cost_summary,
                    config.token_tracker, type="MCTS Sim Configure Join",
                )
                joined_columns = get_columns_join(cfg_res[0])
                configured_step = f"JOIN : {joined_columns}"

            elif operation == "GROUP_BY/AGGREGATE":
                try:
                    if rag_hints_step:
                        config.logger.info(
                            f"[simulate/op] RAG hints retrieved for configure_groupby at step {step} "
                            f"(prefix depth={len(sim_history)})"
                        )
                    cfg_prompt = get_prompt(
                        prompt_type="group_by_aggregate",
                        max_tokens=config.token_limit,
                        model=config.model,
                        allowed_operation_list=OPERATOR_TYPES,
                        operation_history=sim_history,
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
                        source_length=config.source_length,
                        aggregate_flag=aggregate_flag,
                        aggregate_hints_truncate=aggregate_hints_truncate,
                        hint_source=config.hint_source,
                        few_shot=few_shot,
                        fd_flag=int(config.fd_flag),
                        static_hints=getattr(config, "static_hints", True),
                        nth_intermediate_step=step + 1 if intermediate_materialization else 0,
                        intermediate_scores=intermediate_scores,
                        data_split=getattr(config, "data_split", "test"),
                        rag_hints=rag_hints_step,
                    )
                except Exception:
                    config.logger.warning(
                        f"[simulate/op] group_by_aggregate prompt failed (step {step}): "
                        f"{traceback.format_exc()}"
                    )
                    step += 1
                    continue
                cfg_res = query_gpt(
                    config.llm_client, config.model, [cfg_prompt],
                    config.q_count, config.logger, config.cost_summary,
                    config.token_tracker, type="MCTS Sim Configure GroupBy",
                )
                # mirrors multi_step.py line 481: raw cleaned JSON, no prefix
                configured_step = re.sub(r"```json\n|\n|```", "", cfg_res[0])

            elif operation == "UNION":
                try:
                    if rag_hints_step:
                        config.logger.info(
                            f"[simulate/op] RAG hints retrieved for configure_union at step {step} "
                            f"(prefix depth={len(sim_history)})"
                        )
                    cfg_prompt = get_prompt(
                        prompt_type="union",
                        max_tokens=config.token_limit,
                        model=config.model,
                        allowed_operation_list=OPERATOR_TYPES,
                        operation_history=sim_history,
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
                        source_length=config.source_length,
                        hint_source=config.hint_source,
                        few_shot=few_shot,
                        fd_flag=int(config.fd_flag),
                        static_hints=getattr(config, "static_hints", True),
                        nth_intermediate_step=step + 1 if intermediate_materialization else 0,
                        intermediate_scores=intermediate_scores,
                        data_split=getattr(config, "data_split", "test"),
                        rag_hints=rag_hints_step,
                    )
                except Exception:
                    config.logger.warning(
                        f"[simulate/op] union prompt failed (step {step}): "
                        f"{traceback.format_exc()}"
                    )
                    step += 1
                    continue
                cfg_res = query_gpt(
                    config.llm_client, config.model, [cfg_prompt],
                    config.q_count, config.logger, config.cost_summary,
                    config.token_tracker, type="MCTS Sim Configure Union",
                )
                tables_ = get_columns(cfg_res[0])
                configured_step = f"UNION : {tables_}"

            elif operation == "PIVOT":
                configured_step = "PIVOT"

            elif operation == "UNPIVOT":
                configured_step = "UNPIVOT"

            else:
                config.logger.warning(
                    f"[simulate/op] Unknown operator '{operation}' at step {step} — skipping"
                )
                step += 1
                continue

            sim_history.append(configured_step)
            config.logger.info(
                f"[simulate/op] step {step}: appended '{configured_step[:80]}'"
            )
            step += 1

            # ── Intermediate materialization ──────────────────────────────
            if intermediate_materialization:
                interm_csv = (
                    f"{config.directory}/length{config.len_idx_target_idx}"
                    f"/intermediate_step{step}.csv"
                )
                _simulate_get_python(
                    sim_history, target_file_location, state,
                    csv_save_path=interm_csv,
                    nth_intermediate_step=step,
                    intermediate_scores=intermediate_scores,
                    is_final=False,
                )
                if os.path.exists(interm_csv):
                    try:
                        df_interm = pd.read_csv(interm_csv, low_memory=False)
                        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
                        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
                        _, col_ratio_s, _, fd_f1_s, true_combined_s, debug_dict_s = \
                            value_based_relative_csv_score_timed(df_interm, df_gt)
                        nl_score_s = build_nl_score_interpretation(
                            fd_f1_s, col_ratio_s, true_combined_s, debug_dict_s
                        )
                        intermediate_scores[step] = (true_combined_s, nl_score_s)
                        config.logger.info(
                            f"[simulate/op] Intermediate score at step {step}: "
                            f"{true_combined_s:.4f}"
                        )
                    except Exception:
                        config.logger.warning(
                            f"[simulate/op] Intermediate scoring failed at step {step}: "
                            f"{traceback.format_exc()}"
                        )

        else:
            config.logger.warning(
                f"[simulate/op] Iter {state['iteration']}: "
                f"hit step limit ({_MAX_SIMULATE_STEPS}) without NO_MORE_OPERATION"
            )

    script, response = _simulate_get_python(
        sim_history, target_file_location, state,
        nth_intermediate_step=len(sim_history),
        intermediate_scores=intermediate_scores,
        is_final=True,
    )
    return script, response, sim_history


def _simulate_pipeline_level(state: "MCTSGraphState") -> tuple:
    """
    Pipeline-level simulation (original behaviour): given the expanded node's
    operation history, ask the LLM to generate a COMPLETE Python script in one
    shot via the 'mcts_simulate' prompt, then execute it.

    Returns (script: str, response: str, full_history: List[str]).
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]
    target_file_location: str = state["target_file_location"]

    rag_hints = get_rag_hints(
        state.get("local_rag_db_path", ""),
        rollout_history,
    )
    if rag_hints:
        config.logger.info(
            f"[simulate/pipeline] RAG hints retrieved for prefix depth={len(rollout_history)}"
        )

    error_str = ""
    script = ""
    response = ""
    res: List[str] = []

    for trial in range(_MAX_CODE_TRIALS):
        try:
            prompt = get_prompt(
                prompt_type="mcts_simulate",
                max_tokens=config.token_limit,
                model=config.model,
                allowed_operation_list=OPERATOR_TYPES,
                operation_history=rollout_history,
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
                source_length=config.source_length,
                error_string=error_str,
                csv_save_path=target_file_location,
                hint_source=config.hint_source,
                static_hints=getattr(config, "static_hints", True),
                data_split=getattr(config, "data_split", "test"),
                rag_hints=rag_hints,
            )
        except Exception:
            config.logger.warning(
                f"[simulate/pipeline] get_prompt failed (trial {trial}): {traceback.format_exc()}"
            )
            break

        res = query_gpt(
            config.llm_client,
            config.model,
            [prompt],
            config.q_count,
            config.logger,
            config.cost_summary,
            config.token_tracker,
            type="MCTS Simulate",
        )

        pattern = re.compile(r"```[Pp]ython(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res[0])
        if not match:
            error_str += "No valid Python code block found in LLM response.\n"
            config.logger.warning(f"[simulate/pipeline] No code block (trial {trial})")
            continue

        script = match.group(1).strip()
        response = execute_python(script)
        error_str += response + "\n"

        config.logger.info(f"[simulate/pipeline] Trial {trial}: execute_python='{response}'")

        if response == "Success":
            break
    else:
        config.logger.warning(
            f"[simulate/pipeline] Exceeded {_MAX_CODE_TRIALS} trials. "
            f"Last response: '{response}'"
        )

    # Parse the $PLAN$...$END_PLAN$ block from the last LLM response.
    full_history: List[str] = []
    if res:
        plan_match = re.search(r"\$PLAN\$(.*?)\$END_PLAN\$", res[0], re.DOTALL)
        if plan_match:
            full_history = [
                line.strip()
                for line in plan_match.group(1).strip().splitlines()
                if line.strip()
            ]
            config.logger.info(f"[simulate/pipeline] Parsed complete plan: {full_history}")
        else:
            config.logger.warning(
                f"[simulate/pipeline] No $PLAN$ block found in LLM response (iter {state['iteration']})"
            )

    return script, response, full_history


# ─────────────────────────────────────────────────────────────────────────────
# Node 1: mcts_select
# ─────────────────────────────────────────────────────────────────────────────


def mcts_select(state: MCTSGraphState) -> dict:
    """
    Tree Policy (UCB1): walk from root until we reach a node that either
      (a) has untried operator types (not fully expanded), or
      (b) is terminal (NO_MORE_OPERATION leaf).

    Updates: selected_node, selection_path, rollout_history, rollout_step,
             in_rollout, current_operator.
    """
    root: MCTSNode = state["root"]
    config = state["config"]

    max_depth: int = state.get("max_depth", _MAX_SELECT_DEPTH)

    node = root
    path: List[MCTSNode] = [node]

    while (
        not node.is_terminal
        and node.depth < max_depth       # depth-capped nodes are forced leaves
        and node.is_fully_expanded()
        and node.children                # safety: has at least one child
    ):
        # A promising GROUP_BY node may have reaggregation_needed set by backprop.
        # Stop here to add more AGGREGATE variants instead of descending.
        if (
            node.operator_type == "GROUP_BY"
            and node.reaggregation_needed
            and len(node.children) < AGGREGATE_MAX_CHILDREN
        ):
            node.reaggregation_needed = False
            config.logger.info(
                f"[MCTS Select] Iter {state['iteration']}: "
                f"GROUP_BY reaggregation triggered at depth={len(path)-1} "
                f"({len(node.children)}/{AGGREGATE_MAX_CHILDREN} AGGREGATE children) — "
                f"stopping to expand more variants"
            )
            break
        node = node.best_child()
        path.append(node)

    config.logger.info(
        f"[MCTS Select] Iter {state['iteration']}: "
        f"selected depth={len(path) - 1}, op={node.operator_type}, "
        f"visits={node.visits}, children={len(node.children)}"
    )

    return {
        "selected_node": node,
        "selection_path": path,
        "rollout_history": list(node.operation_history),
        "rollout_step": len(node.operation_history),
        "in_rollout": False,
        "current_operator": "",
        "current_script": "",
        "current_score": 0.0,
        "current_response": "",
        "critique_attempted": False,  # reset each iteration
        "log_messages": state["log_messages"]
        + [
            f"Iter {state['iteration']}: selected node depth={len(path)-1} op={node.operator_type}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 2: next_operator_step  (EXPANSION — single mcts_expand LLM call)
# ─────────────────────────────────────────────────────────────────────────────


def next_operator_step(state: MCTSGraphState) -> dict:
    """
    EXPANSION (Option B — batch expand, single simulate):
    One mcts_expand LLM call returns k ranked candidates. ALL new candidates
    are immediately added to the tree as children (0 visits each). Only the
    LLM's #1 priority candidate is simulated this iteration; the rest wait
    for future UCB1 selection.

    Logic
    -----
    1. Ask the LLM for MAX_CHILDREN candidates (always, to fill all slots).
       NO_MORE_OPERATION is excluded from the allowed operators here so expansion
       always grows the tree — only simulation and critique may terminate a plan.
    2. Add every candidate whose configured_step is not already a child.
    3. If GROUP_BY is in the uncovered operator types, also inject one deterministic
       hint-driven GROUP_BY candidate from hints_v3 statistical checks (runs always,
       regardless of hint_source — reads source CSVs directly, no LLM call).
    4. If no new configs were added, mark node saturated.
    5. Simulate only candidates[0] (top priority), whether it is new or existing.
    6. Ultimate fallback (empty/unparseable response): saturate silently, re-simulate
       from existing prefix.
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]
    selected_node: MCTSNode = state["selected_node"]
    selection_path: List[MCTSNode] = state["selection_path"]

    # Always ask for MAX_CHILDREN candidates so we can fill all tree slots at once.
    k = MCTSNode.MAX_CHILDREN

    # Determine whether this is a forced AGGREGATE expansion (parent is GROUP_BY)
    # or a standard structural expansion.
    # • GROUP_BY parent  → only AGGREGATE is valid next; use aggregation expand prompt.
    # • All other nodes  → propose only structural op types not yet covered as children,
    #                       so each type gets exactly one attempt before the node is
    #                       considered fully expanded.
    is_groupby_expansion = (selected_node.operator_type == "GROUP_BY")
    explored_steps = list(selected_node.children.keys())  # configs already in tree

    if is_groupby_expansion:
        expand_prompt_type = "mcts_expand_aggregate"
        expand_ops = ["AGGREGATE"]
    else:
        expand_prompt_type = "mcts_expand"
        covered_op_types = {c.operator_type for c in selected_node.children.values()}
        expand_ops = [op for op in STRUCTURAL_EXPAND_OPS if op not in covered_op_types]
        if not expand_ops:
            # Safety guard: all types already covered — shouldn't reach here in
            # normal flow since is_fully_expanded() would have been True.
            expand_ops = list(STRUCTURAL_EXPAND_OPS)
        # NO_MORE_OPERATION is intentionally NOT offered here — expansion should
        # always grow the tree; only simulation/critique may terminate a plan
        # (the simulate prompt explicitly handles "no more steps needed").
        # Offering it here just added redundant candidates that either sit at
        # 0 visits forever (never selected) or pick up phantom virtual visits
        # with q=0.000 from backpropagate()'s divergence bookkeeping.

    # ── RAG: fetch similar-case hints for the current pipeline prefix ─────
    # Skip at depth 0: no operation history to query on, and all operators are
    # candidates anyway — RAG hints would be uninformative noise.
    rag_hints = []
    if rollout_history:
        rag_hints = get_rag_hints(
            state.get("local_rag_db_path", ""),
            rollout_history,
        )
    if rag_hints:
        config.logger.info(
            f"[expand] RAG hints retrieved for prefix depth={len(rollout_history)}"
        )
    elif not rollout_history:
        config.logger.info("[expand] depth=0 — RAG skipped")

    # ── Single LLM call: get k ranked candidates with configurations ──────
    try:
        prompt = get_prompt(
            prompt_type=expand_prompt_type,
            max_tokens=config.token_limit,
            model=config.model,
            allowed_operation_list=expand_ops,
            operation_history=rollout_history,
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
            source_length=config.source_length,
            hint_source=config.hint_source,
            fd_flag=int(config.fd_flag),
            mcts_expand_k=k,
            data_split=getattr(config, "data_split", "test"),
            rag_hints=rag_hints,
            explored_steps=explored_steps,
        )
    except Exception:
        config.logger.warning(
            f"[expand] get_prompt (mcts_expand) raised: {traceback.format_exc()}"
        )
        prompt = None

    _cost_budget_exhausted = False
    if prompt is not None:
        try:
            res = query_gpt(
                config.llm_client,
                config.model,
                [prompt],
                config.q_count,
                config.logger,
                config.cost_summary,
                config.token_tracker,
                type="MCTS Expand",
            )
            candidates = get_mcts_candidates(res[0], expand_ops)
        except CostBudgetExceeded as e:
            config.logger.warning(f"[expand] {e} — stopping search.")
            _cost_budget_exhausted = True
            candidates = []
    else:
        candidates = []

    config.logger.info(
        f"[expand] Iter {state['iteration']}: "
        f"mode={'aggregate' if is_groupby_expansion else 'standard'} "
        f"candidates={[(op, cfg[:50]) for op, cfg in candidates]}"
    )

    # ── Batch-add all new candidates to the tree ──────────────────────────
    # Children are keyed by the FULL configured_step string.
    existing_configs: set = set(selected_node.children.keys())
    new_configs_added: List[str] = []

    for op_type, cfg in candidates:
        if cfg not in existing_configs:
            child_history = rollout_history + [cfg]
            selected_node.add_child(cfg, child_history, operator_type=op_type)
            new_configs_added.append(cfg)
            existing_configs.add(cfg)  # keep local set consistent
            config.logger.info(
                f"[expand] Iter {state['iteration']}: added child op={op_type} "
                f"cfg={cfg[:60]} "
                f"(tree now has {len(selected_node.children)} children)"
            )

    # ── FD-based GROUP BY candidate (pre-computed from target table keys) ────
    # Injected first (before LLM and hints_v3) so it gets simulated first when
    # it is new. Derived from functional-dependency analysis of the target table.
    _fd_cfg_new: Optional[str] = None  # set when FD candidate is freshly added this iter
    if not is_groupby_expansion and "GROUP_BY" in expand_ops:
        fd_cfg = getattr(config, "hint_groupby_fd_candidate", None)
        if fd_cfg and fd_cfg not in existing_configs:
            child_history = rollout_history + [fd_cfg]
            selected_node.add_child(fd_cfg, child_history, operator_type="GROUP_BY")
            new_configs_added.append(fd_cfg)
            existing_configs.add(fd_cfg)
            _fd_cfg_new = fd_cfg
            config.logger.info(
                f"[expand] Iter {state['iteration']}: added FD-based GROUP_BY "
                f"cfg={fd_cfg[:100]}"
            )

    # ── hints_v3 GROUP_BY candidate ───────────────────────────────────────────
    # Added after FD candidate (lower priority). Derived from statistical checks
    # on source data. Pre-computed once at case start (30 s timeout).
    if not is_groupby_expansion and "GROUP_BY" in expand_ops:
        hint_cfg = getattr(config, "hint_groupby_v3_candidate", None)
        if hint_cfg and hint_cfg not in existing_configs:
            child_history = rollout_history + [hint_cfg]
            selected_node.add_child(hint_cfg, child_history, operator_type="GROUP_BY")
            new_configs_added.append(hint_cfg)
            existing_configs.add(hint_cfg)
            config.logger.info(
                f"[expand] Iter {state['iteration']}: added hints_v3 GROUP_BY "
                f"cfg={hint_cfg[:100]}"
            )

    # Saturation: LLM returned no new configs — mark so selection descends past this node
    if not new_configs_added and candidates:
        selected_node.saturated = True
        config.logger.info(
            f"[expand] Iter {state['iteration']}: all candidates already in tree — "
            f"node marked saturated"
        )

    # ── Simulation target priority: FD candidate > LLM #1 > fallback ─────────
    # If an FD candidate was freshly added this iteration, simulate it first.
    # Otherwise fall back to the LLM's top-ranked candidate.
    if _fd_cfg_new:
        chosen_op, chosen_cfg = "GROUP_BY", _fd_cfg_new
        new_history = rollout_history + [chosen_cfg]
        new_node = selected_node.children[chosen_cfg]
        config.logger.info(
            f"[expand] Iter {state['iteration']}: simulating FD-based GROUP_BY first "
            f"| cfg={chosen_cfg[:80]} "
            f"({len(new_configs_added)} new child(ren) added this iteration)"
        )
    elif candidates:
        chosen_op, chosen_cfg = candidates[0]
        new_history = rollout_history + [chosen_cfg]

        # Navigate to the top-priority child (guaranteed to exist after batch-add above)
        if chosen_cfg not in selected_node.children:
            new_node = selected_node.add_child(
                chosen_cfg, new_history, operator_type=chosen_op
            )
        else:
            new_node = selected_node.children[chosen_cfg]

        config.logger.info(
            f"[expand] Iter {state['iteration']}: simulating LLM top-priority op={chosen_op} "
            f"| cfg={chosen_cfg[:80]} "
            f"({len(new_configs_added)} new child(ren) added this iteration)"
        )
    else:
        # Ultimate fallback: no parseable candidates at all.
        # Saturate the node silently — NO_MORE_OPERATION is never added to the tree.
        # Simulate from the existing prefix; simulation/critique decide termination.
        selected_node.saturated = True
        new_node = selected_node
        new_history = rollout_history
        chosen_op = selected_node.operator_type or ""
        config.logger.warning(
            f"[expand] Iter {state['iteration']}: no valid candidates parsed, "
            f"node marked saturated — re-simulating from existing prefix"
        )

    return {
        "rollout_history": new_history,
        "rollout_step": len(new_history),
        "current_operator": chosen_op,
        "in_rollout": True,
        "selection_path": selection_path + [new_node],
        "selected_node": new_node,
        "terminal_found": state["terminal_found"],
        "cost_budget_exhausted": _cost_budget_exhausted,
        "log_messages": state["log_messages"]
        + [
            f"[EXPAND] iter={state['iteration']} op={chosen_op} configured={chosen_cfg if candidates else '(fallback)'}"
            + (" COST_BUDGET_EXHAUSTED" if _cost_budget_exhausted else "")
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 3: simulate  (SIMULATION phase)
# ─────────────────────────────────────────────────────────────────────────────


def simulate(state: MCTSGraphState) -> dict:
    """
    SIMULATION: dispatch to operator-level or pipeline-level simulation based
    on state["simulation_mode"] ("operator" | "pipeline", default "pipeline").

    Operator-level  — iterates get_next_operator + configure prompts one step
                      at a time (mirrors multi_step.py), then generates code.
    Pipeline-level  — original behaviour: one mcts_simulate LLM call completes
                      the whole pipeline + code in a single prompt.

    Updates: current_script, current_response, current_full_history.
    """
    config = state["config"]
    sim_mode = state.get("simulation_mode", "pipeline")

    # Merge any consecutive GROUP_BY + AGGREGATE tree steps into the single
    # GROUP_BY/AGGREGATE format that simulation and code-gen prompts understand.
    merged_history = _merge_groupby_aggregate(state["rollout_history"])
    if merged_history != state["rollout_history"]:
        config.logger.info(
            f"[simulate] Iter {state['iteration']}: "
            f"merged GROUP_BY+AGGREGATE in rollout_history "
            f"({len(state['rollout_history'])} → {len(merged_history)} steps)"
        )
        state = {**state, "rollout_history": merged_history}

    config.logger.info(
        f"[simulate] Iter {state['iteration']}: "
        f"mode={sim_mode}, history={state['rollout_history']}"
    )

    try:
        if sim_mode == "operator":
            script, response, full_history = _simulate_operator_level(state)
        else:
            script, response, full_history = _simulate_pipeline_level(state)
    except CostBudgetExceeded as e:
        config.logger.warning(f"[simulate] {e} — stopping search.")
        return {
            "cost_budget_exhausted": True,
            "current_script": "",
            "current_response": "cost_budget_exhausted",
            "current_full_history": [],
            "log_messages": state["log_messages"]
            + [f"[SIMULATE] iter={state['iteration']} COST_BUDGET_EXHAUSTED — no request sent"],
        }

    _result = "Success" if response == "Success" else "FAILED"

    return {
        "current_script": script,
        "current_response": response,
        "current_full_history": full_history,
        "log_messages": state["log_messages"]
        + [
            f"[SIMULATE] iter={state['iteration']} mode={sim_mode} result={_result} "
            f"plan_steps={len(full_history)}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 4: execute_and_score
# ─────────────────────────────────────────────────────────────────────────────


def execute_and_score(state: MCTSGraphState) -> dict:
    """
    Load the CSV written by the generated script, compare with ground truth
    using relative_csv_score for reward, and compute hard validation for stop
    criteria (`validation_passed`).

    Updates: current_score, best_score, best_script, best_operation_history,
             validation_passed.
    """
    config = state["config"]

    # Short-circuit: budget was exhausted before any LLM call this iteration.
    if state.get("cost_budget_exhausted", False):
        config.logger.info("[execute_and_score] cost_budget_exhausted — skipping scoring.")
        return {"current_score": 0.0, "judge_verdict": False}

    response = state["current_response"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    validation_mode = state.get("validation_mode", "hard_match")
    rollout_history = state["rollout_history"]

    reward = 0.0
    iteration_validation_passed = False
    judge_verdict = False
    reward_mode = state.get("reward_mode", "score")
    llm_judge = state.get("llm_judge", "none")
    score_components = None

    if response == "Success":
        try:
            reward, iteration_validation_passed, score_components = _score_and_validate_output(
                target_file_location=target_file_location,
                ground_truth_location=ground_truth_location,
                validation_mode=validation_mode,
                reward_mode=reward_mode,
                gt_cache_path=state.get("gt_score_cache_path", ""),
                score_weights=state.get("score_weights"),
            )
            # --no_score_threshold: suppress early-stop for continuous score modes
            # so the search exhausts its full budget and picks the best at the end.
            if (
                state.get("no_score_threshold", False)
                and reward_mode in ("score", "det_score_value")
            ):
                iteration_validation_passed = False
        except Exception:
            config.logger.warning(
                f"[execute_and_score] Scoring/validation failed: {traceback.format_exc()}"
            )

        if llm_judge != "none":
            try:
                df_output = pd.read_csv(target_file_location, low_memory=False)
                df_gt = pd.read_csv(ground_truth_location, low_memory=False)
                df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
                judge_verdict, _ = llm_judge_fn(
                    df_output, df_gt,
                    judge_type=llm_judge,
                    llm_client=config.llm_client,
                    logger=config.logger,
                )
                iteration_validation_passed = judge_verdict
                config.logger.info(
                    f"[execute_and_score] LLM judge ({llm_judge}): verdict={judge_verdict}"
                )
            except Exception:
                config.logger.warning(
                    f"[execute_and_score] LLM judge failed: {traceback.format_exc()}"
                )

    validation_passed = state.get("validation_passed", False) or iteration_validation_passed

    _components_str = (
        "components={" + ", ".join(f"{k}={v}" for k, v in score_components.items()) + "}"
        if score_components else "components=None"
    )
    config.logger.info(
        f"[execute_and_score] Iter {state['iteration']}: "
        f"reward={reward:.4f} (mode={reward_mode}), validation_passed={validation_passed}, "
        f"{_components_str}, history={rollout_history}"
    )

    # Update global best.
    # Use the LLM's complete plan (current_full_history) as the operation history when
    # available — it captures the full pipeline the LLM reasoned about (including steps
    # beyond rollout_history). Fall back to rollout_history if the plan block was absent.
    best_score = state["best_score"]
    best_script = state["best_script"]
    best_op_hist = state["best_operation_history"]
    full_history = state["current_full_history"] or list(rollout_history)

    if iteration_validation_passed:
        # Validation is the primary success signal: keep best_* aligned with the
        # script that actually validated, even on score ties.
        best_score = reward
        best_script = state["current_script"]
        best_op_hist = full_history
        config.logger.info(
            f"[execute_and_score] Validation passed; promoting script as best "
            f"(reward={reward:.4f}, complete_plan={full_history})"
        )
    elif reward > best_score:
        best_score = reward
        best_script = state["current_script"]
        best_op_hist = full_history
        config.logger.info(
            f"[execute_and_score] New best: reward={reward:.4f}, "
            f"complete_plan={full_history}"
        )

    return {
        "current_score": reward,
        "pre_critique_score": reward,
        "validation_passed": validation_passed,
        "judge_verdict": judge_verdict,
        "best_score": best_score,
        "best_script": best_script,
        "best_operation_history": best_op_hist,
        "latest_script": state["current_script"],  # always track last executed script
        "log_messages": state["log_messages"]
        + [
            f"Iter {state['iteration']}: "
            f"reward={reward:.4f} (mode={reward_mode}) "
            f"validation_passed={validation_passed} "
            f"judge_verdict={judge_verdict} history={rollout_history}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 5: backpropagate
# ─────────────────────────────────────────────────────────────────────────────


def backpropagate(state: MCTSGraphState) -> dict:
    """
    Dual-pass backpropagation:
    1. Simulate's actual path (capped at expanded node's depth): rewarded with pre_critique_score
    2. Critique path (capped at expanded node's depth): rewarded with critique_score

    Pass 1 uses the LLM's $PLAN$ (current_full_history) truncated to the expanded
    node's depth, so reward is credited to the path the LLM actually chose rather
    than the expansion candidate path.  Nodes are walked/created in the tree as
    needed via _find_or_create_path; the depth cap prevents simulation from growing
    the tree beyond the current expansion frontier.

    Tree mutations are in-place on MCTSNode objects.
    Updates: iteration (incremented by 1).
    """
    selection_path: List[MCTSNode] = state["selection_path"]
    script: str = state["current_script"]
    config = state["config"]
    root: MCTSNode = state["root"]

    pre_critique_score: float = state.get("pre_critique_score", state.get("current_score", 0.0))
    critique_selection_path: List[MCTSNode] = state.get("critique_selection_path", [])
    critique_score: float = state.get("critique_score", 0.0)

    # ── Resolve the path that simulation actually walked ──────────────────────
    # current_full_history is the LLM's $PLAN$ (may differ from rollout_history).
    # We cap it at the expanded node's depth so simulation never grows the tree
    # beyond the expansion frontier.
    full_history: List[str] = state.get("current_full_history", [])
    expanded_depth: int = len(state.get("rollout_history", []))  # = depth of expanded node

    # Split any merged GROUP_BY/AGGREGATE steps back into separate GROUP_BY + AGGREGATE
    # nodes so the tree stays consistent with the expand-layer structure.
    full_history = _split_groupby_aggregate(full_history)

    sim_backprop_path: List[MCTSNode] = selection_path  # default: no divergence
    sim_diverged: bool = False
    selection_only_nodes: List[MCTSNode] = []  # nodes on selection path but not sim path

    if full_history and expanded_depth > 0:
        truncated_sim = full_history[:expanded_depth]
        try:
            built_path = _find_or_create_path(root, truncated_sim)
            if truncated_sim != list(state.get("rollout_history", [])):
                # Simulation chose a different route than what UCB1 selected.
                # Credit the simulation's actual path with the real reward.
                # The selection path nodes that simulation never visited get a
                # virtual visit (reward=0) — just enough to make their UCB1
                # finite so selection rotates away from them instead of returning
                # indefinitely with UCB1=∞.  No quality signal is implied.
                sim_backprop_path = built_path
                sim_diverged = True
                built_ids = {id(n) for n in built_path}
                selection_only_nodes = [n for n in selection_path if id(n) not in built_ids]
                config.logger.info(
                    f"[backpropagate] Iter {state['iteration']}: sim path diverged — "
                    f"crediting sim path with reward={pre_critique_score:.4f}, "
                    f"giving {len(selection_only_nodes)} selection-only nodes a virtual visit (0)"
                )
        except Exception:
            config.logger.warning(
                f"[backpropagate] Iter {state['iteration']}: "
                f"failed to build sim path — using selection_path: {traceback.format_exc()}"
            )

    # ── Pass 1: Backprop pre-critique score ──────────────────────────────────
    config.logger.info(
        f"[backpropagate] Iter {state['iteration']}: "
        f"Pass 1 ({'sim' if sim_diverged else 'selection'} path): "
        f"{len(sim_backprop_path)} nodes, reward={pre_critique_score:.4f}"
    )
    # Capture old best BEFORE update() promotes it — used for script caching below.
    _sim_leaf_old_best = sim_backprop_path[-1].best_score if sim_backprop_path else float('inf')
    for node in reversed(sim_backprop_path):
        node.update(pre_critique_score)
        if (
            node.operator_type == "GROUP_BY"
            and pre_critique_score >= _REAGGREGATION_REWARD_THRESHOLD
            and len(node.children) < AGGREGATE_MAX_CHILDREN
        ):
            node.reaggregation_needed = True
            config.logger.info(
                f"[backpropagate] Iter {state['iteration']}: "
                f"GROUP_BY reaggregation flagged "
                f"(score={pre_critique_score:.4f}, "
                f"children={len(node.children)}/{AGGREGATE_MAX_CHILDREN})"
            )

    # Virtual visits for selection-only nodes when simulation diverged
    for node in reversed(selection_only_nodes):
        node.update(0.0)  # visits += 1, total_reward += 0 → UCB1 becomes finite

    # Cache best script on the deepest simulated node if improved.
    # Compare against the OLD best (before update() promoted it), otherwise the
    # strict '>' check is never True on the first visit of a node.
    if sim_backprop_path and pre_critique_score > _sim_leaf_old_best:
        sim_backprop_path[-1].best_script = script

    # ── Pass 2: Backprop critique score to critique path (if it exists) ──────
    if critique_selection_path:
        config.logger.info(
            f"[backpropagate] Iter {state['iteration']}: "
            f"Pass 2 (critique path): {len(critique_selection_path)} nodes, reward={critique_score:.4f}"
        )
        # Capture old best BEFORE update() promotes it.
        _crit_leaf_old_best = critique_selection_path[-1].best_score
        for node in reversed(critique_selection_path):
            node.update(critique_score)  # in-place: visits += 1, total_reward += reward
            if (
                node.operator_type == "GROUP_BY"
                and critique_score >= _REAGGREGATION_REWARD_THRESHOLD
                and len(node.children) < AGGREGATE_MAX_CHILDREN
            ):
                node.reaggregation_needed = True

        # Cache best script on the deepest critique node if improved.
        if critique_score > _crit_leaf_old_best:
            critique_selection_path[-1].best_script = script

    # ── Update iteration and no-improvement counter ──
    new_iteration = state["iteration"] + 1
    prev_best = state["best_score"]
    # Use max of both scores (pre-critique or critique) to check improvement
    max_score = max(pre_critique_score, critique_score) if critique_selection_path else pre_critique_score
    new_best = state["best_score"] if max_score <= prev_best else max_score
    if new_best > prev_best:
        no_improvement_count = 0
    else:
        no_improvement_count = state.get("no_improvement_count", 0) + 1

    config.logger.info(
        f"[backpropagate] Iter {state['iteration']} done. "
        f"pre_critique_reward={pre_critique_score:.4f}, "
        f"critique_reward={critique_score:.4f}, "
        f"root.visits={sim_backprop_path[0].visits if sim_backprop_path else 0}, "
        f"next_iter={new_iteration}, no_improvement_count={no_improvement_count}"
    )

    # Per-iteration tree snapshot — printed every iteration so timeouts still
    # capture the last complete iteration's state.
    _reward_path = root.best_reward_path()
    _leaf = _reward_path[-1]
    config.logger.info(
        f"[MCTS Iter {state['iteration']} Summary] "
        f"best_score_so_far={new_best:.4f}, "
        f"reward_path_depth={_leaf.depth}, "
        f"reward_path_ops={_leaf.operation_history}, "
        f"leaf_total_reward={_leaf.total_reward:.4f}, "
        f"leaf_script_cached={'yes' if _leaf.best_script else 'no'}, "
        f"root_visits={root.visits}, root_total_reward={root.total_reward:.4f}"
    )
    config.logger.info(f"[MCTS Tree Iter {state['iteration']}] {root.to_dict()}")

    return {
        "iteration": new_iteration,
        "no_improvement_count": no_improvement_count,
        "log_messages": state["log_messages"]
        + [
            f"Backprop iter {state['iteration']}: "
            f"pre_critique={pre_critique_score:.4f}, critique={critique_score:.4f}, "
            f"paths=({len(sim_backprop_path)}, {len(critique_selection_path)})"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 6: extract_best
# ─────────────────────────────────────────────────────────────────────────────


def extract_best(state: MCTSGraphState) -> dict:
    """
    MCTS search complete. Determine the final script as the GLOBAL best-scoring
    script seen anywhere during the search (tracked incrementally in
    state["best_score"]/state["best_script"] by execute_and_score() and
    mcts_critique() — "Method A" / max-score selection), rather than walking
    root.best_reward_path() (greedy descent by accumulated total_reward) and
    taking that leaf's locally-cached script.

    Tree exploration (UCB1 selection, dual-pass critique backprop) is
    unchanged — only which script gets extracted as the final answer changes.
    """
    config = state["config"]
    main_folder = state["main_folder"]
    experiment_name = state["experiment_name"]
    case_id = state["case_id"]
    root: MCTSNode = state["root"]

    best_script = state["best_script"]
    best_score = state["best_score"]
    best_op_history = state["best_operation_history"]

    if not best_script:
        config.logger.warning(
            f"[extract_best] Global best_script is empty "
            f"(best_score={best_score:.4f}). "
            f"This should not happen if any iteration executed successfully."
        )

    # Diagnostic only: log how the accumulated-reward path would have differed,
    # to make divergence between the two selection strategies visible in logs.
    reward_path = root.best_reward_path()
    reward_leaf = reward_path[-1]
    config.logger.info(
        f"[MCTS Complete] global best_score={best_score:.4f}, ops={best_op_history} | "
        f"(for comparison) best-reward-path leaf: depth={reward_leaf.depth}, "
        f"leaf_total_reward={reward_leaf.total_reward:.4f}, "
        f"leaf_best_score={reward_leaf.best_score:.4f}, "
        f"total_root_visits={root.visits}, "
        f"tree_depth_explored={len(root.best_path())}"
    )
    config.logger.info(f"[MCTS Tree] {root.to_dict()}")

    # "best" mode: critique the final script once before saving
    if (
        getattr(config, "mcts_critique_mode", "none") == "best"
        and best_script
        and best_score < 1.0
    ):
        config.logger.info(
            f"[extract_best] Running 'best' mode critique on final script "
            f"(score={best_score:.4f})"
        )
        crit_script, crit_score, _, _, _, _ = _run_critique_llm(state, best_script)
        if crit_score > best_score:
            config.logger.info(
                f"[extract_best] Critique improved score: {best_score:.4f} → {crit_score:.4f}"
            )
            best_score = crit_score
            best_script = crit_script
        else:
            config.logger.info(
                f"[extract_best] Critique did not improve score ({crit_score:.4f} ≤ {best_score:.4f}), keeping original"
            )

    # Save best script
    if best_script:
        script_dir = os.path.join(main_folder, f"length{case_id}", "script_archive")
        os.makedirs(script_dir, exist_ok=True)
        archive_path = os.path.join(script_dir, f"{experiment_name}_mcts.py")
        recovery_path = os.path.join(
            main_folder, f"length{case_id}", "python_recovered_mcts.py"
        )
        for path in (archive_path, recovery_path):
            with open(path, "w") as f:
                f.write(best_script)
        config.logger.info(f"[extract_best] Scripts saved to {archive_path}")

    return {
        "best_script": best_script,
        "best_score": best_score,
        "best_operation_history": best_op_history,
        "log_messages": state["log_messages"]
        + [
            f"MCTS complete after {state['iteration']} iterations. "
            f"Global best_score={best_score:.4f}, ops={best_op_history}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Critique helpers
# ─────────────────────────────────────────────────────────────────────────────


def _build_critique_prompt(state: MCTSGraphState, script: str, rag_hints: str = "") -> str:
    """
    Build the single-call critique prompt by filling in all $PLACEHOLDERS$.
    Uses config fields populated in mcts_search.py (source_information, fd_hints, etc.).
    Returns the filled prompt string, or empty string on error.
    """
    config = state["config"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    rollout_history = state["rollout_history"]

    prompt_path = os.path.join(_ROOT, "prompts", "mcts_critique.txt")
    try:
        with open(prompt_path) as f:
            prompt = f.read()
    except Exception:
        config.logger.warning(f"[critique] Could not read prompt file: {prompt_path}")
        return ""

    prompt = prompt.replace(
        "$SRC_INFO$", getattr(config, "source_information", "") or ""
    )
    prompt = prompt.replace(
        "$SCHEMA$",
        config.target_data_schema_with_types or config.target_data_schema,
    )
    prompt = prompt.replace("$EXAMPLES$", config.target_samples)
    prompt = prompt.replace("$OPERATIONS$", "\n".join(rollout_history))
    prompt = prompt.replace("$CURRENT_SCRIPT$", script)
    prompt = prompt.replace("$CSV_SAVE_PATH$", target_file_location)
    prompt = prompt.replace("$FD_HINT$", getattr(config, "fd_hints", "") or "")

    # Ground truth row count
    try:
        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
        prompt = prompt.replace("$NUM_TUPLES$", str(len(df_gt)))
    except Exception:
        prompt = prompt.replace("$NUM_TUPLES$", "N/A")

    # Current output info (may not exist if script failed entirely)
    try:
        df_res = pd.read_csv(target_file_location, low_memory=False)
        prompt = prompt.replace("$RES_SCHEMA$", ", ".join(df_res.columns))
        prompt = prompt.replace("$NUM_RES_TUPLES$", str(len(df_res)))
        prompt = prompt.replace(
            "$RES_EXAMPLES$",
            df_res.head(config.target_length).to_string(index=False),
        )
    except Exception:
        prompt = prompt.replace("$RES_SCHEMA$", "N/A (script execution failed)")
        prompt = prompt.replace("$NUM_RES_TUPLES$", "N/A")
        prompt = prompt.replace("$RES_EXAMPLES$", "N/A")

    # Inject critique hints unless suppressed via --no_static_hints
    if getattr(config, "static_hints", True):
        try:
            from hints.hints_static import get_hints_section, CRITIQUE_HINT_IDS
            prompt = prompt.replace(
                "$STATIC_HINTS$", get_hints_section(CRITIQUE_HINT_IDS, fmt="numbered")
            )
        except Exception:
            prompt = prompt.replace("$STATIC_HINTS$", "")
    else:
        prompt = prompt.replace("$STATIC_HINTS$", "")

    if rag_hints:
        prompt += f"\n{rag_hints.rstrip()}\n"

    return prompt


def _run_critique_llm(state: MCTSGraphState, script: str):
    """
    Build + send the critique prompt.
    Returns (new_script, new_score, new_response, validation_passed, critique_plan, score_components).
    Loads ground truth internally for scoring. score_components is the 4 raw
    (unweighted) score_1 inputs (det_score_value mode only), or None.
    critique_plan is a List[str] parsed from $PLAN$...$END_PLAN$ block, or [] if not found.
    """
    config = state["config"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    validation_mode = state.get("validation_mode", "hard_match")

    prompt = _build_critique_prompt(state, script, rag_hints="")
    if not prompt:
        return script, state.get("current_score", 0.0), "Prompt build failed", False, [], None

    res = query_gpt(
        config.llm_client,
        config.model,
        [prompt],
        config.q_count,
        config.logger,
        config.cost_summary,
        config.token_tracker,
        type="MCTS Critique",
    )

    # Parse $PLAN$...$END_PLAN$ block
    critique_plan: List[str] = []
    plan_match = re.search(r"\$PLAN\$(.*?)\$END_PLAN\$", res[0], re.DOTALL)
    if plan_match:
        critique_plan = [
            line.strip()
            for line in plan_match.group(1).strip().splitlines()
            if line.strip()
        ]
        config.logger.info(f"[_run_critique_llm] Parsed critique plan: {critique_plan}")

    pattern = re.compile(r"```[Pp]ython(.*?)```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(res[0])
    new_script = match.group(1).strip() if match else ""

    new_score = state.get("current_score", 0.0)
    new_response = "No code extracted"
    validation_passed = False
    score_components = None

    if new_script:
        new_response = execute_python(new_script)
        if new_response == "Success":
            try:
                reward_mode = state.get("reward_mode", "score")
                new_score, validation_passed, score_components = _score_and_validate_output(
                    target_file_location=target_file_location,
                    ground_truth_location=ground_truth_location,
                    validation_mode=validation_mode,
                    reward_mode=reward_mode,
                    score_weights=state.get("score_weights"),
                )
            except Exception:
                new_score = 0.0
                validation_passed = False

    return new_script, new_score, new_response, validation_passed, critique_plan, score_components


# ─────────────────────────────────────────────────────────────────────────────
# Node 7: mcts_critique  (CRITIQUE phase — single LLM call)
# ─────────────────────────────────────────────────────────────────────────────


def mcts_critique(state: MCTSGraphState) -> dict:
    """
    CRITIQUE (single LLM call): analyzes the failed/imperfect script and outputs
    corrected Python code + operation plan. Triggered when current_score < 1.0 in "simulate" mode.
    Re-executes and re-scores the corrected script before backpropagation.

    NEW: Parses the $PLAN$...$END_PLAN$ block from critique response, walks/creates
    the tree nodes for that plan, and returns critique_selection_path for separate
    backpropagation.
    """
    config = state["config"]

    # Should never be reached (should_critique short-circuits), but guard defensively.
    if state.get("cost_budget_exhausted", False):
        config.logger.info("[mcts_critique] cost_budget_exhausted — skipping critique.")
        return {"critique_attempted": True}

    config.logger.info(
        f"[mcts_critique] Iter {state['iteration']}: "
        f"critiquing script (score={state['current_score']:.4f})"
    )

    new_script, new_score, new_response, critique_validation_passed, critique_plan, new_score_components = _run_critique_llm(
        state, state["current_script"]
    )

    _crit_components_str = (
        "components={" + ", ".join(f"{k}={v}" for k, v in new_score_components.items()) + "}"
        if new_score_components else "components=None"
    )
    config.logger.info(
        f"[mcts_critique] Iter {state['iteration']}: "
        f"score {state['current_score']:.4f} → {new_score:.4f}, {_crit_components_str}"
    )

    # Build critique_selection_path by walking/creating tree nodes for critique_plan,
    # capped at the expanded node's depth so critique never grows the tree beyond
    # the current expansion frontier.
    # Split merged GROUP_BY/AGGREGATE steps so tree nodes match expand-layer structure.
    expanded_depth: int = len(state.get("rollout_history", []))
    critique_selection_path: List[MCTSNode] = []
    if critique_plan:
        critique_plan = _split_groupby_aggregate(critique_plan)
        truncated_critique_plan = critique_plan[:expanded_depth] if expanded_depth > 0 else []
        try:
            if truncated_critique_plan:
                critique_selection_path = _find_or_create_path(state["root"], truncated_critique_plan)
            config.logger.info(
                f"[mcts_critique] Critique path created: {len(critique_selection_path)} nodes "
                f"(plan_len={len(critique_plan)} → capped at depth={expanded_depth}), "
                f"plan={[s[:60] for s in truncated_critique_plan[:3]]}"
            )
        except Exception:
            config.logger.warning(
                f"[mcts_critique] Failed to build critique path: {traceback.format_exc()}"
            )

    # If LLM judge is active, re-run it on the critiqued output to get an updated verdict.
    judge_verdict = state.get("judge_verdict", False)
    llm_judge = state.get("llm_judge", "none")
    if llm_judge != "none" and new_script and new_response == "Success":
        try:
            df_output = pd.read_csv(state["target_file_location"], low_memory=False)
            df_gt = pd.read_csv(state["ground_truth_location"], low_memory=False)
            df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
            judge_verdict, _ = llm_judge_fn(
                df_output, df_gt,
                judge_type=llm_judge,
                llm_client=config.llm_client,
                logger=config.logger,
            )
            critique_validation_passed = judge_verdict
            config.logger.info(
                f"[mcts_critique] LLM judge ({llm_judge}) after critique: verdict={judge_verdict}"
            )
        except Exception:
            config.logger.warning(
                f"[mcts_critique] LLM judge failed after critique: {traceback.format_exc()}"
            )

    best_score = state["best_score"]
    best_script = state["best_script"]
    best_op_hist = state["best_operation_history"]
    full_history = state["current_full_history"] or list(state["rollout_history"])
    validation_passed = state.get("validation_passed", False) or critique_validation_passed
    selected_script = new_script if new_script else state["current_script"]
    if critique_validation_passed:
        # Same rule as execute_and_score: a validated script should be the final best.
        best_score = new_score
        best_script = selected_script
        best_op_hist = full_history
    elif new_score > best_score:
        best_score = new_score
        best_script = selected_script
        best_op_hist = full_history

    return {
        "current_script": selected_script,
        "current_score": new_score,
        "critique_score": new_score,
        "critique_selection_path": critique_selection_path,
        "current_response": new_response,
        "critique_attempted": True,
        "judge_verdict": judge_verdict,
        "validation_passed": validation_passed,
        "best_score": best_score,
        "best_script": best_script,
        "best_operation_history": best_op_hist,
        "log_messages": state["log_messages"]
        + [
            f"[CRITIQUE] iter={state['iteration']} "
            f"score_before={state['current_score']:.4f} score_after={new_score:.4f} "
            f"judge_verdict={judge_verdict} validation_passed={validation_passed} "
            f"critique_path_len={len(critique_selection_path)}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Conditional edge functions
# ─────────────────────────────────────────────────────────────────────────────


def should_critique(state: MCTSGraphState) -> str:
    """
    After execute_and_score:
    - if cost_budget_exhausted, skip critique and let backpropagate → check_budget stop the search
    - if ground-truth validation already passed this iteration, skip critique
      and proceed to backpropagate (search will stop in check_budget)
    - "simulate" mode → critique if score < 1.0 and not yet attempted this iteration
    - "none" / "best" mode → always skip to backpropagate
    """
    if state.get("cost_budget_exhausted", False):
        return "backpropagate"

    if state.get("validation_passed", False):
        return "backpropagate"

    mode = getattr(state["config"], "mcts_critique_mode", "none")
    llm_judge = state.get("llm_judge", "none")
    reward_mode = state.get("reward_mode", "score")

    if mode == "simulate" and not state.get("critique_attempted", False):
        if llm_judge != "none":
            needs_critique = not state.get("judge_verdict", False)
        else:
            critique_threshold = 0.9 if reward_mode == "score" else 1.0
            needs_critique = state["current_score"] < critique_threshold
        if needs_critique:
            return "critique"
    return "backpropagate"


def reuse_terminal_reward(state: MCTSGraphState) -> dict:
    """
    A NO_MORE_OPERATION node was selected that has already been simulated at least
    once.  Skip re-simulation entirely: backpropagate the cached best_score so the
    tree statistics stay consistent without spending another LLM call.
    """
    node: MCTSNode = state["selected_node"]
    config = state["config"]
    config.logger.info(
        f"[reuse_terminal] Iter {state['iteration']}: "
        f"reusing cached reward={node.best_score:.4f} for NO_MORE_OPERATION node "
        f"(visits={node.visits}, depth={len(node.operation_history)})"
    )
    return {
        "current_score": node.best_score,
        "pre_critique_score": node.best_score,
        "current_script": node.best_script,
        "current_full_history": list(node.operation_history),
        "current_response": "Success" if node.best_script else "",
        # Clear stale critique state from previous iterations
        "critique_selection_path": [],
        "critique_score": 0.0,
        "critique_attempted": True,  # prevent critique from triggering on reused reward
        "log_messages": state["log_messages"]
        + [
            f"[REUSE_TERMINAL] iter={state['iteration']} "
            f"cached_reward={node.best_score:.4f} depth={len(node.operation_history)}"
        ],
    }


def is_selected_terminal(state: MCTSGraphState) -> str:
    """
    After mcts_select:
    - terminal node (NO_MORE_OPERATION) or depth-capped node (depth >= max_depth):
        visits > 0 → reuse cached reward (no LLM call)
        visits == 0 → simulate for the first time
    - non-terminal and within depth cap: expand with next_operator_step
    """
    node: MCTSNode = state["selected_node"]
    max_depth: int = state.get("max_depth", _MAX_SELECT_DEPTH)
    is_leaf = node.is_terminal or node.depth >= max_depth
    if is_leaf:
        if node.visits > 0:
            return "reuse_terminal"
        return "terminal"
    return "expand"


def check_budget(state: MCTSGraphState) -> str:
    """
    After backpropagate: stop when any termination condition is met.

    Cost-budget mode (cost_budget > 0):
      - Always stop on validation_passed.
      - Stop when cumulative cost >= cost_budget.
      - If early_stopping > 0, also stop on score plateau.
      - Iteration cap (max_iterations) is ignored.

    Iteration mode (cost_budget == 0, original behavior):
      - Always stop on validation_passed.
      - Stop on score plateau (early_stopping iterations with no improvement).
      - Stop on hard iteration cap (max_iterations).
    """
    config = state["config"]

    # Always: stop if LLMClient blocked a request (budget reached before sending)
    if state.get("cost_budget_exhausted", False):
        current_cost = config.token_tracker.cost_summary()["total_cost"]
        config.logger.warning(
            f"[check_budget] cost_budget_exhausted flag set at iter {state['iteration']} "
            f"(spent=${current_cost:.6f}) — stopping."
        )
        return "done"

    # Always: stop if a correct result was validated
    if state.get("validation_passed", False):
        config.logger.info(
            f"[check_budget] Validation passed at iter {state['iteration']} — stopping."
        )
        return "done"

    # Stop if any leaf node (no children) has been visited >= 5 times.
    # A leaf visited that many times means the same path keeps getting selected;
    # further iterations are wasteful.
    _root = state.get("root")
    if _root is not None and _root.visits > 0:
        _stack = list(_root.children.values())
        while _stack:
            _n = _stack.pop()
            if not _n.children and _n.visits >= 5:
                _op_label = _n.operation_history[-1] if _n.operation_history else "?"
                config.logger.info(
                    f"[check_budget] Leaf node saturated "
                    f"(visits={_n.visits}>=5, op={_op_label!r}) — stopping early."
                )
                return "done"
            _stack.extend(_n.children.values())

    no_improvement_count = state.get("no_improvement_count", 0)
    early_stopping = state.get("early_stopping", 5)
    cost_budget = state.get("cost_budget", 0.0)

    if cost_budget > 0.0:
        # ── Cost-budget mode ──────────────────────────────────────────────
        current_cost = config.token_tracker.cost_summary()["total_cost"]
        if current_cost >= cost_budget:
            config.logger.warning(
                f"[check_budget] Cost budget ${cost_budget:.4f} reached "
                f"(spent=${current_cost:.6f}) at iter {state['iteration']} — stopping."
            )
            return "done"
        # Plateau check is optional: early_stopping == 0 disables it
        if early_stopping > 0 and no_improvement_count >= early_stopping:
            config.logger.info(
                f"[check_budget] No improvement for {no_improvement_count} consecutive iterations "
                f"(best_score={state['best_score']:.4f}, early_stopping={early_stopping}) — stopping early."
            )
            return "done"
        return "iterate"

    else:
        # ── Iteration mode (original behavior) ───────────────────────────
        if early_stopping > 0 and no_improvement_count >= early_stopping:
            config.logger.info(
                f"[check_budget] No improvement for {no_improvement_count} consecutive iterations "
                f"(best_score={state['best_score']:.4f}, early_stopping={early_stopping}) — stopping early."
            )
            return "done"
        if state["iteration"] >= state["max_iterations"]:
            config.logger.warning(
                f"[check_budget] Hard cap ({state['max_iterations']} iterations) reached — stopping."
            )
            return "done"
        return "iterate"
