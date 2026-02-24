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

from auto_suggest_llm_util import (
    calculate_score,
    get_columns,
    get_columns_join,
    get_operation,
    get_prompt,
    query_gpt,
)
from mcts_node import MCTSNode, OPERATOR_TYPES
from state import MCTSGraphState
from util.utils import execute_python

# Maximum tree selection depth (used in mcts_select only)
_MAX_SELECT_DEPTH = 15
# Maximum code-generation retries inside simulate
_MAX_CODE_TRIALS = 5


# ─────────────────────────────────────────────────────────────────────────────
# Helper: ask LLM for next operator
# ─────────────────────────────────────────────────────────────────────────────

def _ask_operator(state: MCTSGraphState, operation_history: List[str]) -> str:
    """
    Call the LLM to select the next operator given current operation_history.
    Returns one of the OPERATOR_TYPES strings, or "NO_MORE_OPERATION" on error.
    """
    config = state["config"]
    try:
        prompt = get_prompt(
            prompt_type="get_next_operator",
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
            hint_source=config.hint_source,
            few_shot=state.get("few_shot", 0),
        )
    except Exception:
        config.logger.warning(f"[_ask_operator] get_prompt raised: {traceback.format_exc()}")
        return "NO_MORE_OPERATION"

    res = query_gpt(
        config.llm_client,
        config.model,
        prompt,
        config.q_count,
        config.logger,
        config.cost_summary,
        config.token_tracker,
        type="MCTS Ask Operator",
    )
    operation = get_operation(res[0])
    if operation not in OPERATOR_TYPES or not operation:
        config.logger.warning(
            f"[_ask_operator] Unexpected operator '{operation}', defaulting to NO_MORE_OPERATION"
        )
        return "NO_MORE_OPERATION"
    return operation


# ─────────────────────────────────────────────────────────────────────────────
# Helper: configure the chosen operator
# ─────────────────────────────────────────────────────────────────────────────

def _configure_operator(
    state: MCTSGraphState, operator_type: str, operation_history: List[str]
) -> str:
    """
    Ask the LLM to configure the given operator.
    Returns the full operation string to append to operation_history.
    E.g. "JOIN : [col_a = col_b]" or "GROUP_BY/AGGREGATE : {...}"
    """
    config = state["config"]

    # Operators that need no LLM configuration
    if operator_type in ("PIVOT", "UNPIVOT", "NO_MORE_OPERATION"):
        return operator_type

    prompt_type_map = {
        "JOIN": "join",
        "UNION": "union",
        "GROUP_BY/AGGREGATE": "group_by_aggregate",
    }
    prompt_type = prompt_type_map.get(operator_type)
    if not prompt_type:
        return operator_type

    try:
        prompt = get_prompt(
            prompt_type=prompt_type,
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
            join_flag=state.get("join_flag", 0),
            join_hints_truncate=state.get("join_hints_truncate", []),
            aggregate_flag=state.get("aggregate_flag", 0),
            aggregate_hints_truncate=state.get("aggregate_hints_truncate", []),
            hint_source=config.hint_source,
        )
    except Exception:
        config.logger.warning(
            f"[_configure_operator] get_prompt raised for {operator_type}: {traceback.format_exc()}"
        )
        return operator_type  # fallback: just use bare operator name

    res = query_gpt(
        config.llm_client,
        config.model,
        prompt,
        config.q_count,
        config.logger,
        config.cost_summary,
        config.token_tracker,
        type=f"MCTS Configure {operator_type}",
    )

    raw = res[0]
    if operator_type == "JOIN":
        detail = get_columns_join(raw)
        return f"JOIN : {detail}"
    elif operator_type == "GROUP_BY/AGGREGATE":
        # The group_by_aggregate prompt returns a JSON blob
        return re.sub(r"```json\n|\n|```", "", raw).strip()
    elif operator_type == "UNION":
        detail = get_columns(raw)
        return f"UNION : {detail}"
    return operator_type


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
        f"visits={node.visits}, untried={node.untried_operators()}"
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
        "log_messages": state["log_messages"] + [
            f"Iter {state['iteration']}: selected node depth={len(path)-1} op={node.operator_type}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 2: next_operator_step  (EXPANSION only — one operator per iteration)
# ─────────────────────────────────────────────────────────────────────────────

def next_operator_step(state: MCTSGraphState) -> dict:
    """
    EXPANSION: ask the LLM for one operator, configure it, add it to the tree.

    This is the only operator-selection call per MCTS iteration.
    After this, simulate() immediately takes the expanded history and generates
    a complete pipeline + code — no further operator steps occur.

    Tree update logic
    -----------------
    - If the LLM suggests an operator type not yet tried at selected_node
      → create a new child node (true expansion).
    - If the operator type already has a child (tried in a previous iteration)
      → follow the existing branch (the simulation will still run from here,
        providing a fresh reward sample for backpropagation).
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]   # selected_node.operation_history
    selected_node: MCTSNode = state["selected_node"]
    selection_path: List[MCTSNode] = state["selection_path"]

    # Ask LLM for the next operator type
    operator_type = _ask_operator(state, rollout_history)

    config.logger.info(
        f"[expand] Iter {state['iteration']}: op={operator_type}, "
        f"depth={len(rollout_history)}"
    )

    # Configure the operator (adds join cols, group-by spec, etc.)
    configured_op = _configure_operator(state, operator_type, rollout_history)
    new_history = rollout_history + [configured_op]

    # Add to / follow the tree
    if operator_type not in selected_node.children:
        new_node = selected_node.add_child(operator_type, new_history)
        config.logger.info(f"[expand] New child created: op={operator_type}")
    else:
        new_node = selected_node.children[operator_type]
        config.logger.info(f"[expand] Following existing child: op={operator_type}")

    return {
        "rollout_history": new_history,
        "rollout_step": len(new_history),
        "current_operator": operator_type,
        "in_rollout": True,
        "selection_path": selection_path + [new_node],
        "selected_node": new_node,
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
    rollout_history: List[str] = state["rollout_history"]   # expanded node's history
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
                prompt_type="python_script",
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
            prompt,
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

        config.logger.info(
            f"[simulate] Trial {trial}: execute_python='{response}'"
        )

        if response == "Success":
            break
    else:
        config.logger.warning(
            f"[simulate] Exceeded {_MAX_CODE_TRIALS} trials. "
            f"Last response: '{response}'"
        )

    return {
        "current_script": script,
        "current_response": response,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 4: execute_and_score
# ─────────────────────────────────────────────────────────────────────────────

def execute_and_score(state: MCTSGraphState) -> dict:
    """
    Load the CSV written by the generated script, compare with ground truth
    using calculate_score, and use the result as the MCTS reward.

    Updates: current_score, best_score, best_script, best_operation_history.
    """
    config = state["config"]
    response = state["current_response"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    rollout_history = state["rollout_history"]

    score = 0.0
    if response == "Success":
        try:
            df_output = pd.read_csv(target_file_location, low_memory=False)
            df_gt = pd.read_csv(ground_truth_location, low_memory=False)
            # Drop the pandas auto-index column
            df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
            score = calculate_score(df_gt, df_output)
        except Exception:
            config.logger.warning(
                f"[execute_and_score] Scoring failed: {traceback.format_exc()}"
            )
            score = 0.0

    config.logger.info(
        f"[execute_and_score] Iter {state['iteration']}: "
        f"score={score:.4f}, history={rollout_history}"
    )

    # Update global best
    best_score = state["best_score"]
    best_script = state["best_script"]
    best_op_hist = state["best_operation_history"]
    if score > best_score:
        best_score = score
        best_script = state["current_script"]
        best_op_hist = list(rollout_history)

    return {
        "current_score": score,
        "best_score": best_score,
        "best_script": best_script,
        "best_operation_history": best_op_hist,
        "log_messages": state["log_messages"] + [
            f"Iter {state['iteration']}: score={score:.4f} history={rollout_history}"
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
    config.logger.info(
        f"[backpropagate] Iter {state['iteration']} done. "
        f"reward={reward:.4f}, path_len={len(selection_path)}, "
        f"root.visits={selection_path[0].visits if selection_path else 0}, "
        f"next_iter={new_iteration}"
    )

    return {
        "iteration": new_iteration,
        "log_messages": state["log_messages"] + [
            f"Backprop iter {state['iteration']}: reward={reward:.4f}"
        ],
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
        "log_messages": state["log_messages"] + [
            f"MCTS complete after {state['iteration']} iterations. "
            f"Best score={best_score:.4f}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Conditional edge functions
# ─────────────────────────────────────────────────────────────────────────────

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
    After backpropagate: continue MCTS if budget remains, otherwise extract best.
    """
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    return "iterate"
