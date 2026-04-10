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

from auto_suggest_llm_util import (
    get_mcts_candidates,
    get_prompt,
    query_gpt,
)
from eval_score.score import relative_csv_score
from mcts_node import MCTSNode, OPERATOR_TYPES
from state import MCTSGraphState
from util.utils import execute_python
from validation.hard_match import compare_lists_matching, compare_tables_matching
from validation.fuzzy_match import compare_tables_fuzzy

# Maximum tree selection depth (used in mcts_select only)
_MAX_SELECT_DEPTH = 15
# Maximum code-generation retries inside simulate
_MAX_CODE_TRIALS = 5
# Hard timeout (seconds) for the full scoring + validation call
_SCORE_TIMEOUT = 60


def _score_worker(target_file_location: str, ground_truth_location: str, result_queue):
    """Subprocess worker: load CSVs and compute score, put result in queue.

    Accepts file paths instead of DataFrames to avoid pickling overhead.
    """
    try:
        df_output = pd.read_csv(target_file_location, low_memory=False)
        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
        _, col_ratio, _, fd_f1, _, _ = relative_csv_score(df_output, df_gt)
        result_queue.put((fd_f1 + col_ratio) / 2)
    except Exception:
        result_queue.put(0.0)


def _score_with_timeout(target_file_location: str, ground_truth_location: str) -> float:
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
        args=(target_file_location, ground_truth_location, q),
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


def _score_and_validate_output(
    target_file_location: str,
    ground_truth_location: str,
    validation_mode: str,
    reward_mode: str,
):
    """
    Load output + ground truth and compute only the metric required by reward_mode:
      - "score"      : relative_csv_score (FD + column map + distribution)
      - "validation" : avg_similarity from compare_lists/tables_matching (per-col × per-row)
      - "partial"    : fuzzy column-match ratio from compare_tables_fuzzy

    Returns (reward, is_correct) where is_correct is derived from reward == 1.0.
    """
    df_output = pd.read_csv(target_file_location, low_memory=False)
    df_gt = pd.read_csv(ground_truth_location, low_memory=False)
    df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

    if reward_mode == "validation":
        validate_fn = (
            compare_tables_matching if validation_mode == "autopipeline" else compare_lists_matching
        )
        avg_similarity, is_correct, _, _ = validate_fn(df_output, df_gt)
        return float(avg_similarity), bool(is_correct)

    elif reward_mode == "partial":
        partial, _ = compare_tables_fuzzy(df_output, df_gt)
        return float(partial), partial == 1.0

    else:  # "score"
        score = _score_with_timeout(target_file_location, ground_truth_location)
        return score, score >= 1.0


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

    node = root
    path: List[MCTSNode] = [node]

    while (
        not node.is_terminal
        and node.is_fully_expanded()
        and node.children  # safety: has at least one child
        and len(path) <= _MAX_SELECT_DEPTH
    ):
        node = node.best_child()
        path.append(node)

    config.logger.info(
        f"[MCTS Select] Iter {state['iteration']}: "
        f"selected depth={len(path) - 1}, op={node.operator_type}, "
        f"visits={node.visits}, children={len(node.children)}/{MCTSNode.MAX_CHILDREN}"
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
    2. Add every candidate whose configured_step is not already a child.
    3. If no new configs were added, mark node saturated.
    4. Simulate only candidates[0] (top priority), whether it is new or existing.
    5. Ultimate fallback (empty/unparseable response): NO_MORE_OPERATION + saturated.
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]
    selected_node: MCTSNode = state["selected_node"]
    selection_path: List[MCTSNode] = state["selection_path"]

    # Always ask for MAX_CHILDREN candidates so we can fill all tree slots at once.
    k = MCTSNode.MAX_CHILDREN

    # ── Single LLM call: get k ranked candidates with configurations ──────
    try:
        prompt = get_prompt(
            prompt_type="mcts_expand",
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
            hint_source=config.hint_source,
            fd_flag=int(config.fd_flag),
            mcts_expand_k=k,
        )
    except Exception:
        config.logger.warning(
            f"[expand] get_prompt (mcts_expand) raised: {traceback.format_exc()}"
        )
        prompt = None

    if prompt is not None:
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
        candidates = get_mcts_candidates(res[0], OPERATOR_TYPES)
    else:
        candidates = []

    config.logger.info(
        f"[expand] Iter {state['iteration']}: "
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
                f"(tree now has {len(selected_node.children)}/{MCTSNode.MAX_CHILDREN} children)"
            )

    # Saturation: LLM returned no new configs — mark so selection descends past this node
    if not new_configs_added and candidates:
        selected_node.saturated = True
        config.logger.info(
            f"[expand] Iter {state['iteration']}: all candidates already in tree — "
            f"node marked saturated"
        )

    # ── Simulation target: always the LLM's #1 priority candidate ─────────
    if candidates:
        chosen_op, chosen_cfg = candidates[0]
    else:
        # Ultimate fallback: no parseable candidates at all
        chosen_op = "NO_MORE_OPERATION"
        chosen_cfg = "NO_MORE_OPERATION"
        selected_node.saturated = True
        config.logger.warning(
            f"[expand] Iter {state['iteration']}: no valid candidates parsed, "
            f"node marked saturated, falling back to NO_MORE_OPERATION"
        )

    config.logger.info(
        f"[expand] Iter {state['iteration']}: simulating top-priority op={chosen_op} "
        f"| cfg={chosen_cfg[:80]} "
        f"({len(new_configs_added)} new child(ren) added this iteration)"
    )

    new_history = rollout_history + [chosen_cfg]

    # Navigate to the top-priority child (guaranteed to exist after batch-add above)
    if chosen_cfg not in selected_node.children:
        new_node = selected_node.add_child(
            chosen_cfg, new_history, operator_type=chosen_op
        )
    else:
        new_node = selected_node.children[chosen_cfg]

    is_terminal_expansion = chosen_op == "NO_MORE_OPERATION"

    return {
        "rollout_history": new_history,
        "rollout_step": len(new_history),
        "current_operator": chosen_op,
        "in_rollout": True,
        "selection_path": selection_path + [new_node],
        "selected_node": new_node,
        "terminal_found": state["terminal_found"] or is_terminal_expansion,
        "log_messages": state["log_messages"]
        + [
            f"[EXPAND] iter={state['iteration']} op={chosen_op} configured={chosen_cfg}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 3: simulate  (SIMULATION phase)
# ─────────────────────────────────────────────────────────────────────────────


def simulate(state: MCTSGraphState) -> dict:
    """
    SIMULATION: given the expanded node's operation history, ask the LLM to
    generate a COMPLETE Python script that implements the full transformation
    pipeline, then execute it.

    Why this is correct
    -------------------
    After expansion, rollout_history contains the one newly-added operator
    (e.g. ["JOIN : [order_id = order_id]"]).  The python_script prompt hands
    this partial plan to the LLM and asks it to produce working Python code
    that achieves the target schema — the LLM decides what additional steps
    are needed inside the code.  This is the pipeline-completion step.

    Retries up to _MAX_CODE_TRIALS times, feeding execution errors back into
    the prompt so the LLM can self-correct.

    Updates: current_script, current_response.
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]  # expanded node's history
    target_file_location: str = state["target_file_location"]

    config.logger.info(
        f"[simulate] Iter {state['iteration']}: "
        f"completing pipeline from history={rollout_history}"
    )

    error_str = ""
    script = ""
    response = ""

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
            )
        except Exception:
            config.logger.warning(
                f"[simulate] get_prompt failed (trial {trial}): {traceback.format_exc()}"
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

        # Extract Python code block
        pattern = re.compile(r"```[Pp]ython(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res[0])
        if not match:
            error_str += "No valid Python code block found in LLM response.\n"
            config.logger.warning(f"[simulate] No code block (trial {trial})")
            continue

        script = match.group(1).strip()
        response = execute_python(script)
        error_str += response + "\n"

        config.logger.info(f"[simulate] Trial {trial}: execute_python='{response}'")

        if response == "Success":
            break
    else:
        config.logger.warning(
            f"[simulate] Exceeded {_MAX_CODE_TRIALS} trials. "
            f"Last response: '{response}'"
        )

    _trials = trial + 1  # trial retains last loop value; range(5) guarantees it is set
    _result = "Success" if response == "Success" else "FAILED"

    # Parse the $PLAN$...$END_PLAN$ block from the last LLM response.
    # This is the LLM's complete operation sequence (partial history + any extra steps
    # it reasoned about + NO_MORE_OPERATION). Fall back to [] if absent or unparseable.
    full_history: List[str] = []
    if res:
        plan_match = re.search(r"\$PLAN\$(.*?)\$END_PLAN\$", res[0], re.DOTALL)
        if plan_match:
            full_history = [
                line.strip()
                for line in plan_match.group(1).strip().splitlines()
                if line.strip()
            ]
            config.logger.info(f"[simulate] Parsed complete plan: {full_history}")
        else:
            config.logger.warning(
                f"[simulate] No $PLAN$ block found in LLM response (iter {state['iteration']})"
            )

    return {
        "current_script": script,
        "current_response": response,
        "current_full_history": full_history,
        "log_messages": state["log_messages"]
        + [
            f"[SIMULATE] iter={state['iteration']} trials={_trials} result={_result} "
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
    response = state["current_response"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    validation_mode = state.get("validation_mode", "hard_match")
    rollout_history = state["rollout_history"]

    reward = 0.0
    iteration_validation_passed = False
    reward_mode = state.get("reward_mode", "score")
    if response == "Success":
        try:
            reward, iteration_validation_passed = _score_and_validate_output(
                target_file_location=target_file_location,
                ground_truth_location=ground_truth_location,
                validation_mode=validation_mode,
                reward_mode=reward_mode,
            )
        except Exception:
            config.logger.warning(
                f"[execute_and_score] Scoring/validation failed: {traceback.format_exc()}"
            )

    validation_passed = state.get("validation_passed", False) or iteration_validation_passed

    config.logger.info(
        f"[execute_and_score] Iter {state['iteration']}: "
        f"reward={reward:.4f} (mode={reward_mode}), validation_passed={validation_passed}, "
        f"history={rollout_history}"
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
        "validation_passed": validation_passed,
        "best_score": best_score,
        "best_script": best_script,
        "best_operation_history": best_op_hist,
        "log_messages": state["log_messages"]
        + [
            f"Iter {state['iteration']}: "
            f"reward={reward:.4f} (mode={reward_mode}) "
            f"validation_passed={validation_passed} history={rollout_history}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 5: backpropagate
# ─────────────────────────────────────────────────────────────────────────────


def backpropagate(state: MCTSGraphState) -> dict:
    """
    Walk up selection_path (from expanded node to root), updating each node's
    visit count and total reward.

    Also caches best_script on the deepest node in selection_path if this
    iteration improved the score.

    Tree mutations are in-place on MCTSNode objects.
    Updates: iteration (incremented by 1).
    """
    selection_path: List[MCTSNode] = state["selection_path"]
    reward: float = state["current_score"]
    script: str = state["current_script"]
    config = state["config"]

    # Backpropagate from the expanded/terminal node up to root
    for node in reversed(selection_path):
        node.update(reward)  # in-place: visits += 1, total_reward += reward

    # Cache best script on the expanded node (deepest in selection path)
    if selection_path and reward > selection_path[-1].best_score:
        selection_path[-1].best_score = reward
        selection_path[-1].best_script = script

    new_iteration = state["iteration"] + 1
    prev_best = state["best_score"]
    new_best = state["best_score"] if reward <= prev_best else reward
    if new_best > prev_best:
        no_improvement_count = 0
    else:
        no_improvement_count = state.get("no_improvement_count", 0) + 1

    config.logger.info(
        f"[backpropagate] Iter {state['iteration']} done. "
        f"reward={reward:.4f}, path_len={len(selection_path)}, "
        f"root.visits={selection_path[0].visits if selection_path else 0}, "
        f"next_iter={new_iteration}, no_improvement_count={no_improvement_count}"
    )

    return {
        "iteration": new_iteration,
        "no_improvement_count": no_improvement_count,
        "log_messages": state["log_messages"]
        + [f"Backprop iter {state['iteration']}: reward={reward:.4f}"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 6: extract_best
# ─────────────────────────────────────────────────────────────────────────────


def extract_best(state: MCTSGraphState) -> dict:
    """
    MCTS search complete. Extract the best result found across all iterations.
    Saves best script to disk and logs the final tree summary.
    """
    config = state["config"]
    main_folder = state["main_folder"]
    experiment_name = state["experiment_name"]
    case_id = state["case_id"]
    best_score = state["best_score"]
    best_script = state["best_script"]
    best_op_history = state["best_operation_history"]
    root: MCTSNode = state["root"]

    config.logger.info(
        f"[MCTS Complete] best_score={best_score:.4f}, "
        f"best_op_history={best_op_history}, "
        f"total_root_visits={root.visits}, "
        f"tree_depth_explored={len(root.best_path())}"
    )
    config.logger.info(f"[MCTS Tree] {root.to_dict()}")

    # "best" mode: critique the best script once before saving
    if (
        getattr(config, "mcts_critique_mode", "none") == "best"
        and best_script
        and best_score < 1.0
    ):
        config.logger.info(
            f"[extract_best] Running 'best' mode critique on final script "
            f"(score={best_score:.4f})"
        )
        crit_script, crit_score, _, _ = _run_critique_llm(state, best_script)
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
        "log_messages": state["log_messages"]
        + [
            f"MCTS complete after {state['iteration']} iterations. "
            f"Best score={best_score:.4f}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Critique helpers
# ─────────────────────────────────────────────────────────────────────────────


def _build_critique_prompt(state: MCTSGraphState, script: str) -> str:
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

    return prompt


def _run_critique_llm(state: MCTSGraphState, script: str):
    """
    Build + send the critique prompt.
    Returns (new_script, new_score, new_response, validation_passed).
    Loads ground truth internally for scoring.
    """
    config = state["config"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    validation_mode = state.get("validation_mode", "hard_match")

    prompt = _build_critique_prompt(state, script)
    if not prompt:
        return script, state.get("current_score", 0.0), "Prompt build failed", False

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

    pattern = re.compile(r"```[Pp]ython(.*?)```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(res[0])
    new_script = match.group(1).strip() if match else ""

    new_score = state.get("current_score", 0.0)
    new_response = "No code extracted"
    validation_passed = False

    if new_script:
        new_response = execute_python(new_script)
        if new_response == "Success":
            try:
                reward_mode = state.get("reward_mode", "score")
                new_score, validation_passed = _score_and_validate_output(
                    target_file_location=target_file_location,
                    ground_truth_location=ground_truth_location,
                    validation_mode=validation_mode,
                    reward_mode=reward_mode,
                )
            except Exception:
                new_score = 0.0
                validation_passed = False

    return new_script, new_score, new_response, validation_passed


# ─────────────────────────────────────────────────────────────────────────────
# Node 7: mcts_critique  (CRITIQUE phase — single LLM call)
# ─────────────────────────────────────────────────────────────────────────────


def mcts_critique(state: MCTSGraphState) -> dict:
    """
    CRITIQUE (single LLM call): analyzes the failed/imperfect script and outputs
    corrected Python code. Triggered when current_score < 1.0 in "simulate" mode.
    Re-executes and re-scores the corrected script before backpropagation.
    """
    config = state["config"]

    config.logger.info(
        f"[mcts_critique] Iter {state['iteration']}: "
        f"critiquing script (score={state['current_score']:.4f})"
    )

    new_script, new_score, new_response, critique_validation_passed = _run_critique_llm(
        state, state["current_script"]
    )

    config.logger.info(
        f"[mcts_critique] Iter {state['iteration']}: "
        f"score {state['current_score']:.4f} → {new_score:.4f}"
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
        "current_response": new_response,
        "critique_attempted": True,
        "validation_passed": validation_passed,
        "best_score": best_score,
        "best_script": best_script,
        "best_operation_history": best_op_hist,
        "log_messages": state["log_messages"]
        + [
            f"[CRITIQUE] iter={state['iteration']} "
            f"score_before={state['current_score']:.4f} score_after={new_score:.4f} "
            f"validation_passed={validation_passed}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Conditional edge functions
# ─────────────────────────────────────────────────────────────────────────────


def should_critique(state: MCTSGraphState) -> str:
    """
    After execute_and_score:
    - if ground-truth validation already passed this iteration, skip critique
      and proceed to backpropagate (search will stop in check_budget)
    - "simulate" mode → critique if score < 1.0 and not yet attempted this iteration
    - "none" / "best" mode → always skip to backpropagate
    """
    if state.get("validation_passed", False):
        return "backpropagate"

    mode = getattr(state["config"], "mcts_critique_mode", "none")
    reward_mode = state.get("reward_mode", "score")
    critique_threshold = 0.85 if reward_mode == "score" else 1.0
    if (
        mode == "simulate"
        and state["current_score"] < critique_threshold
        and not state.get("critique_attempted", False)
    ):
        return "critique"
    return "backpropagate"


def is_selected_terminal(state: MCTSGraphState) -> str:
    """
    After mcts_select: if the selected node is already a terminal leaf
    (NO_MORE_OPERATION, previously expanded), skip expansion and go directly
    to simulate so MCTS re-samples a reward for this node.
    Otherwise expand with next_operator_step first.
    """
    node: MCTSNode = state["selected_node"]
    if node.is_terminal:
        return "terminal"
    return "expand"


def check_budget(state: MCTSGraphState) -> str:
    """
    After backpropagate: stop when any of the following conditions is met:
      1. Ground-truth validation has passed.
      2. best_score has not improved for 5 consecutive iterations (plateau).
      3. Hard iteration cap (max_iterations) is exhausted.
    Continue otherwise.
    """
    config = state["config"]
    if state.get("validation_passed", False):
        config.logger.info(
            f"[check_budget] Validation passed at iter {state['iteration']} — stopping."
        )
        return "done"
    no_improvement_count = state.get("no_improvement_count", 0)
    early_stopping = state.get("early_stopping", 5)
    if no_improvement_count >= early_stopping:
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
