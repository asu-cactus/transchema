"""
mcts_search: MCTS-based multi-step schema transformation search.

Drop-in replacement for multi_step() in methods/multi_step.py.
Same function signature, same return tuple:
    (is_correct, total_cost, time_elapsed, score, op_hist_)

Usage
-----
    from Langraph.mcts_search import mcts_search

    ms_info = mcts_search(
        args,
        length=2,
        id_=5,
        log_dir_="logs/",
        experiment_name="mcts_run",
        i_=0,
    )

Key args fields
---------------
    args.mcts_iterations    int     MCTS budget (default: 10)
    args.model              str     LLM model identifier
    args.token_limit        int     max tokens per prompt
    args.hint_source        str     "none" | "v1" | "v2"
    args.target_per         float   target sample percentage
    args.is_perc            bool    use percentage sampling?
    args.target_length      int     target sample rows
    args.source_length      int     source sample rows
    args.anon_flag          bool    anonymise schema names?
    args.fd_flag            bool    include functional dependency hints?
    args.join_flag          int     join-hints flag (default 0)
    args.aggregate_flag     int     aggregate-hints flag (default 0)
    args.join_hints_truncate        list[float]  (default [])
    args.aggregate_hints_truncate   list[float]  (default [])
    args.few_shot           int     few-shot examples flag (default 0)
"""

import os
import sys
import time
import traceback

import pandas as pd

# ── Path setup: this file lives in Langraph/, parent is the project root ──────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dataclasses import dataclass
from typing import Any, List

from llm.llm_models import LLMClient, TokenUsageTracker
from log_util.log_util import create_logger
from test_scope import get_test_cases_ids
from util.utils import get_test_info
from validation.hard_match import compare_lists_matching

from mcts_node import MCTSNode
from state import MCTSGraphState
from graph import build_mcts_graph
from viz import write_action_trace, write_tree_viz

# ──────────────────────────────────────────────────────────────────────────────
_MAIN_FOLDER = "autopipeline-benchmarks/github-pipelines"


# ──────────────────────────────────────────────────────────────────────────────
# Config dataclass (mirrors methods/multi_step.py:Config, extended with extras)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class Config:
    """
    Holds all per-case configuration needed by LLM prompt builders and logging.
    Mirrors the Config dataclass in methods/multi_step.py so existing utilities
    (get_prompt, query_gpt, …) work without modification.
    """

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
    llm_client: Any
    q_count: dict
    logger: Any
    cost_summary: list
    token_tracker: Any
    model: str
    token_limit: int


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────


def mcts_search(args, length, id_, log_dir_, experiment_name, i_):
    """
    Run MCTS-based schema transformation for the given test case.

    Parameters
    ----------
    args            : argparse.Namespace — experiment settings
    length          : int — length bucket (e.g. 2 for length2_*)
    id_             : int — case id (e.g. 5 for length*_5)
    log_dir_        : str — directory for log files
    experiment_name : str — label used when saving scripts
    i_              : int — run index (used in script filenames)

    Returns
    -------
    tuple: (is_correct, total_cost, time_elapsed, best_mcts_score, op_hist_str)
    """
    # ── Extract args (with safe defaults for new MCTS-specific fields) ─────
    model = args.model
    token_limit = args.token_limit
    hint_source = args.hint_source
    target_per = args.target_per
    is_perc = args.is_perc
    target_length = args.target_length
    source_length = args.source_length
    anon_flag = args.anon_flag
    fd_flag = args.fd_flag
    max_iterations = getattr(args, "mcts_iterations", 10)
    join_flag = getattr(args, "join_flag", 0)
    aggregate_flag = getattr(args, "aggregate_flag", 0)
    join_hints_truncate = getattr(args, "join_hints_truncate", [])
    aggregate_hints_truncate = getattr(args, "aggregate_hints_truncate", [])
    few_shot = getattr(args, "few_shot", 0)

    # ── Case path and data file selection ──────────────────────────────────
    len_id = length
    target_id = id_
    path_to_files = f"{_MAIN_FOLDER}/length{length}_{id_}/"
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )
    json_file_path = (
        "data/chatgpt_github_ms.json"
        if file_count > 1
        else "data/chatgpt_github_ss.json"
    )

    task_list = get_test_cases_ids(json_file_path, len_id, len_id, target_id, target_id)

    # ── Initialise logging and tracking ────────────────────────────────────
    logger = create_logger("MCTS", log_dir_, len_id, target_id, target_id)
    q_count = {"total": 0, "in_task": 0}

    # Return values (defaults for early-exit paths)
    is_correct = False
    best_score = 0.0
    op_hist_ = ""
    best_script = ""
    start_time = time.time()
    token_tracker = TokenUsageTracker()
    cost_summary: list = []

    # ── Loop over tasks (always exactly one task per case) ─────────────────
    for task in task_list:
        q_count["in_task"] = 0
        logger.info(f"[MCTS] Starting task: {task}")

        cost_summary = []
        start_time = time.time()
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())
        len_idx_target_idx = task[6:]  # strip "length" prefix

        # ── Load case information ─────────────────────────────────────────
        (
            target_data_name,
            target_data_schema,
            target_data_schema_with_types,
            target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        ) = get_test_info(json_file_path, len_idx_target_idx, _MAIN_FOLDER, anon_flag)

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger)

        target_file_location = (
            f"{_MAIN_FOLDER}/length{len_idx_target_idx}/target_multisource_mcts.csv"
        )
        ground_truth_location = f"{_MAIN_FOLDER}/length{len_idx_target_idx}/target.csv"

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
            directory=_MAIN_FOLDER,
        )

        # ── Build initial MCTS state ──────────────────────────────────────
        root = MCTSNode(operation_history=[], parent=None, operator_type=None)

        initial_state: MCTSGraphState = {
            # Problem config
            "config": config,
            "main_folder": _MAIN_FOLDER,
            "ground_truth_location": ground_truth_location,
            "target_file_location": target_file_location,
            "experiment_name": experiment_name,
            "case_id": len_idx_target_idx,
            # Prompt extras
            "join_flag": join_flag,
            "join_hints_truncate": join_hints_truncate,
            "aggregate_flag": aggregate_flag,
            "aggregate_hints_truncate": aggregate_hints_truncate,
            "few_shot": few_shot,
            # Tree-based memory
            "root": root,
            # Iteration control
            "iteration": 0,
            "max_iterations": max_iterations,
            "terminal_found": False,
            # Selection phase (initialised to root)
            "selection_path": [root],
            "selected_node": root,
            # Rollout phase
            "rollout_history": [],
            "rollout_step": 0,
            "in_rollout": False,
            "current_operator": "",
            # Simulation results
            "current_script": "",
            "current_score": 0.0,
            "current_response": "",
            "current_full_history": [],
            # Best result
            "best_script": "",
            "best_score": 0.0,
            "best_operation_history": [],
            # Logging
            "log_messages": [],
        }

        # ── Run MCTS graph ────────────────────────────────────────────────
        logger.info(
            f"[MCTS] Starting search: max_iterations={max_iterations}, "
            f"case={len_idx_target_idx}"
        )
        mcts_graph = build_mcts_graph()
        final_state: MCTSGraphState = mcts_graph.invoke(
            initial_state,
            # Increase recursion limit for deep rollout loops
            config={"recursion_limit": 500},
        )

        # ── Extract results from final state ──────────────────────────────
        best_script = final_state["best_script"]
        best_score = final_state["best_score"]
        op_hist_ = str(final_state["best_operation_history"])

        logger.info(
            f"[MCTS] Search complete. "
            f"best_score={best_score:.4f}, "
            f"best_op_history={op_hist_}, "
            f"root.visits={root.visits}"
        )

        # ── Write visualization files ──────────────────────────────────────
        trace_path = write_action_trace(
            final_state["log_messages"],
            len_idx_target_idx,
            log_dir_,
            best_score=best_score,
            best_history=final_state["best_operation_history"],
        )
        tree_path = write_tree_viz(
            root,
            len_idx_target_idx,
            log_dir_,
            best_history=final_state["best_operation_history"],
        )
        logger.info(f"[MCTS] Action trace → {trace_path}")
        logger.info(f"[MCTS] Tree viz     → {tree_path}")

        # ── Hard accuracy evaluation on best script ────────────────────────
        if best_script:
            try:
                df_output = pd.read_csv(target_file_location, low_memory=False)
                df_gt = pd.read_csv(ground_truth_location, low_memory=False)
                df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
                _, is_correct, _, _ = compare_lists_matching(df_output, df_gt)
            except Exception:
                logger.warning(
                    f"[MCTS] Hard accuracy eval failed: {traceback.format_exc()}"
                )
                is_correct = False

        logger.info(f"[MCTS] Total queries: {q_count['total']}")

    end_time = time.time()
    cost_data = token_tracker.cost_summary()
    total_cost = cost_data.get("total_cost", 0.0)
    time_elapsed = end_time - start_time

    ms_info = (is_correct, total_cost, time_elapsed, best_score, op_hist_)
    print(f"[MCTS] ms_info: {ms_info}")
    return ms_info


# ──────────────────────────────────────────────────────────────────────────────
# Batch runner (python Langraph/mcts_search.py --length 1 --id_start 0 --id_end 100
#                                               --experiment_name my_run)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCTS schema transformation search")
    parser.add_argument(
        "--length", type=int, default=2, help="Length bucket (e.g. 1, 2, 3)"
    )
    parser.add_argument(
        "--id_start", type=int, default=0, help="First case id (inclusive)"
    )
    parser.add_argument(
        "--id_end", type=int, default=0, help="Last case id (inclusive)"
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default="mcts_run",
        help="Experiment label; logs go to logs_langraph/<experiment_name>/",
    )
    parser.add_argument("--model", type=str, default="gpt-4.1-mini")
    parser.add_argument("--token_limit", type=int, default=128000)
    parser.add_argument("--hint_source", type=str, default="none")
    parser.add_argument("--target_per", type=float, default=10.0)
    parser.add_argument("--is_perc", type=bool, default=False)
    parser.add_argument("--target_length", type=int, default=3)
    parser.add_argument("--source_length", type=int, default=3)
    parser.add_argument("--anon_flag", type=bool, default=False)
    parser.add_argument("--fd_flag", type=int, default=0)
    parser.add_argument("--mcts_iterations", type=int, default=15)
    parser.add_argument("--join_flag", type=int, default=0)
    parser.add_argument("--aggregate_flag", type=int, default=0)
    parser.add_argument("--few_shot", type=int, default=0)
    args = parser.parse_args()
    args.join_hints_truncate = []
    args.aggregate_hints_truncate = []

    # Change to project root so relative imports work
    os.chdir(_ROOT)

    # All logs for this run go under a single experiment directory
    log_dir_ = os.path.join("logs_langraph", args.experiment_name)
    os.makedirs(log_dir_, exist_ok=True)

    results = {}
    for case_id in range(args.id_start, args.id_end + 1):
        print(f"\n[MCTS] === length={args.length}  id={case_id} ===")
        try:
            result = mcts_search(
                args,
                length=args.length,
                id_=case_id,
                log_dir_=log_dir_,
                experiment_name=args.experiment_name,
                i_=case_id,
            )
            results[case_id] = result
            print(f"[MCTS] Case {case_id} done: {result}")
        except Exception:
            print(f"[MCTS] Case {case_id} FAILED:\n{traceback.format_exc()}")
            results[case_id] = None

    print("\n[MCTS] === Summary ===")
    for case_id, result in results.items():
        print(f"  id={case_id}: {result}")
