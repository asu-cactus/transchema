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
    args.validation         str     "hard_match" | "autopipeline"
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

import json
import json
import multiprocessing
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
from typing import Any, List, Optional

import tiktoken

from auto_suggest_llm_util import get_source, get_filtered_functional_dependency
from llm.llm_models import LLMClient, TokenUsageTracker
from log_util.log_util import create_logger
from test_scope import get_test_cases_ids
from util.utils import get_test_info, make_test_validation_script
from validation.hard_match import compare_lists_matching, compare_tables_matching

from mcts_node import MCTSNode
from state import MCTSGraphState
from graph import build_mcts_graph
from viz import write_action_trace, write_tree_viz
from rag_pipeline.local_rag_db import build_upper_bound_db, populate_from_global_results

# ──────────────────────────────────────────────────────────────────────────────


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
    # Critique support
    source_information: str   # pre-formatted $SRC_INFO$ string
    static_hints: bool        # True (default) = inject static hints; False = suppress (--no_static_hints)
    fd_hints: str             # pre-formatted FD hint string (empty if fd_flag=0)
    mcts_critique_mode: str   # "none" | "simulate" | "best"
    reward_mode: str          # "score" | "det_score_value" | "validation" | "partial"
    intermediate_materialization: bool  # True = materialize + score at each operator step
    data_split: str = "test"           # "test" or "training" — which CSV prefix to load
    hint_groupby_fd_candidate: Optional[str] = None   # FD-derived GROUP BY step, pre-computed once
    hint_groupby_v3_candidate: Optional[str] = None   # hints_v3-derived GROUP BY step, pre-computed once


# ──────────────────────────────────────────────────────────────────────────────
# FD-based GROUP BY candidate — computed once per case with a hard timeout
# ──────────────────────────────────────────────────────────────────────────────


def _fd_groupby_worker(
    target_file: str,
    source_name_list: List[str],
    source_schema_list: List[str],
    result_queue: "multiprocessing.Queue",
) -> None:
    """Subprocess worker: run FD analysis on target table and return a configured
    GROUP_BY step string, or None if no keys are found / an error occurs."""
    try:
        import os, sys
        _here = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_here)
        _eval_score = os.path.join(_root, "eval_score")
        for _p in (_root, _eval_score):
            if _p not in sys.path:
                sys.path.insert(0, _p)

        import pandas as pd
        from auto_suggest_llm_util import get_filtered_functional_dependency

        df = pd.read_csv(target_file, low_memory=False)
        df = df.drop(df.columns[0], axis=1)

        keys, _fds = get_filtered_functional_dependency(df)

        # Fallback: quality.quality.analyze_functional_dependencies crashes on some
        # tables (TypeError inside GetFDs).  When that happens, get_filtered_functional_dependency
        # silently returns [] — retry with fdtool.main from eval_score/ which is more robust.
        if not keys:
            try:
                import fdtool.fdtool as _fdtool
                from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FTE
                _df_s = df.sample(n=min(1000, len(df)), replace=False).iloc[:, :15]
                with ThreadPoolExecutor(max_workers=1) as _ex:
                    _fut = _ex.submit(_fdtool.main, _df_s)
                    try:
                        _FDs, _E, _raw_keys = _fut.result(timeout=30)
                    except _FTE:
                        _raw_keys = []
                # Take only singleton keys (single-column) at column position 0 or string dtype.
                for _k in _raw_keys:
                    if len(_k) == 1:
                        _col = _k[0]
                        if df.columns.get_loc(_col) == 0 or df[_col].dtype == "object":
                            keys = [_col]
                            break
            except Exception:
                pass

        if not keys:
            result_queue.put(None)
            return

        # Resolve each key column to its source table (table.col format).
        # Falls back to bare column name if not found in any source schema.
        def _find_source_table(col: str) -> Optional[str]:
            for tname, schema in zip(source_name_list, source_schema_list):
                col_names = [p.strip().split()[0] for p in schema.split(",") if p.strip()]
                if col in col_names:
                    return tname
            return None

        qualified = []
        for col in keys:
            tbl = _find_source_table(col)
            qualified.append(f"{tbl}.{col}" if tbl else col)

        result_queue.put(f"GROUP_BY : [{', '.join(qualified)}]")
    except Exception:
        result_queue.put(None)


def _compute_fd_groupby_candidate(
    target_file: str,
    source_name_list: List[str],
    source_schema_list: List[str],
    logger,
    timeout: int = 60,
) -> Optional[str]:
    """Run FD analysis on the target table to derive GROUP BY key columns.

    Executes in a subprocess with a hard *timeout* (default 60 s) to guard
    against cases where the FD algorithm takes very long on wide/large tables.
    The result is returned as a fully configured MCTS step string, e.g.:
        "GROUP_BY : [Source1_9_0.zipcode, Source1_9_0.AGI_STUB]"
    Returns None if analysis times out, finds no keys, or errors.
    """
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_fd_groupby_worker,
        args=(target_file, source_name_list, source_schema_list, result_queue),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        logger.warning(
            f"[FD GROUP BY] Timed out after {timeout}s — skipping FD candidate"
        )
        proc.terminate()
        proc.join()
        return None

    if not result_queue.empty():
        result = result_queue.get()
        if result:
            logger.info(f"[FD GROUP BY] Candidate computed: {result[:120]}")
        return result
    return None


# ──────────────────────────────────────────────────────────────────────────────
# hints_v3 GROUP BY candidate — computed once per case with a hard timeout
# ──────────────────────────────────────────────────────────────────────────────


def _hints_v3_groupby_worker(
    source_name_list: List[str],
    directory: str,
    len_idx_target_idx: str,
    result_queue: "multiprocessing.Queue",
) -> None:
    """Subprocess worker: run hints_v3 statistical checks and return a configured
    GROUP_BY step string, or None if no columns qualify / an error occurs."""
    try:
        import os, sys
        _here = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_here)
        if _root not in sys.path:
            sys.path.insert(0, _root)

        import hints.hint_v3 as _h3
        cols = _h3.get_groupby_hint_columns(source_name_list, directory, len_idx_target_idx)
        if cols:
            result_queue.put(f"GROUP_BY : [{', '.join(cols)}]")
        else:
            result_queue.put(None)
    except Exception:
        result_queue.put(None)


def _compute_hints_v3_groupby_candidate(
    source_name_list: List[str],
    directory: str,
    len_idx_target_idx: str,
    logger,
    timeout: int = 30,
) -> Optional[str]:
    """Run hints_v3 statistical GROUP BY checks with a hard *timeout* (default 30 s).

    hints_v3 reads CSV files and evaluates column-level statistical properties;
    this can be slow on large tables.  The subprocess is hard-killed if it
    exceeds the timeout so it never delays MCTS operations.
    """
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_hints_v3_groupby_worker,
        args=(source_name_list, directory, len_idx_target_idx, result_queue),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        logger.warning(
            f"[hints_v3 GROUP BY] Timed out after {timeout}s — skipping v3 candidate"
        )
        proc.terminate()
        proc.join()
        return None

    if not result_queue.empty():
        result = result_queue.get()
        if result:
            logger.info(f"[hints_v3 GROUP BY] Candidate computed: {result[:120]}")
        return result
    return None


# ──────────────────────────────────────────────────────────────────────────────
# GT scoring cache — pre-computed once per case, reused every iteration
# ──────────────────────────────────────────────────────────────────────────────


def _gt_score_cache_worker(
    ground_truth_location: str,
    cache_path: str,
    result_queue: "multiprocessing.Queue",
) -> None:
    """Subprocess worker: compute GT-side FDs and self-column-map count, write to JSON."""
    try:
        import json, os, sys
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

        _here = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_here)
        _eval_score = os.path.join(_root, "eval_score")
        for _p in (_root, _eval_score):
            if _p not in sys.path:
                sys.path.insert(0, _p)

        import pandas as pd
        import fdtool.fdtool as _fdtool
        import column_map_utils
        from column_map_utils import get_column_map

        MAX_FD_COLS    = 52
        FD_TIMEOUT     = 60
        _MAX_SCORE_COLS = 20
        _MAX_FD_ROWS    = 2000

        def _run_fdtool_local(df):
            """Returns (FDs, E, keys, timed_out)."""
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_fdtool.main, df)
                try:
                    result = future.result(timeout=FD_TIMEOUT)
                    return result[0], result[1], result[2], False
                except FuturesTimeoutError:
                    return [], [], [], True

        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        # Phase 1: try FD mining on the full table (no column/row caps).
        FDs_b, E_b, keys_b, fd_timed_out = _run_fdtool_local(df_gt.iloc[:, :MAX_FD_COLS])

        col_indices = None   # None → no reduction was needed
        max_fd_rows = None

        if fd_timed_out:
            # Phase 2: FD timed out — reduce to 20 evenly-spaced cols + 2000 rows and retry.
            _n   = len(df_gt.columns)
            df_gt = df_gt.iloc[:_MAX_FD_ROWS, :_MAX_SCORE_COLS]
            FDs_b, E_b, keys_b, _ = _run_fdtool_local(df_gt.iloc[:, :MAX_FD_COLS])
            col_indices = list(range(_MAX_SCORE_COLS))
            max_fd_rows = _MAX_FD_ROWS

        column_map_utils.GLOBAL_SUMMARY = None
        self_col_count = len(get_column_map(df_gt, df_gt))

        # Serialize E_b (list of equivalence pairs)
        e_b_serial = []
        for item in E_b:
            try:
                left, right = item
                e_b_serial.append({"left": list(left), "right": list(right)})
            except Exception:
                e_b_serial.append({"raw": str(item)})

        # Serialize keys_b — try direct JSON, fall back to str conversion
        try:
            json.dumps(keys_b)
            keys_b_serial = keys_b
        except (TypeError, ValueError):
            keys_b_serial = [str(k) for k in keys_b] if hasattr(keys_b, "__iter__") else str(keys_b)

        cache = {
            "FDs_b": [{"lhs": list(lhs), "rhs": rhs} for lhs, rhs in FDs_b],
            "E_b": e_b_serial,
            "keys_b": keys_b_serial,
            "self_col_count": self_col_count,
            "col_indices": col_indices,   # list[int] if GT was reduced, else null
            "max_fd_rows": max_fd_rows,   # int if GT was reduced, else null
        }
        with open(cache_path, "w") as f:
            json.dump(cache, f)

        result_queue.put(True)
    except Exception:
        result_queue.put(False)


def _compute_gt_score_cache(
    ground_truth_location: str,
    cache_path: str,
    logger,
    timeout: int = 90,
) -> bool:
    """Pre-compute GT-side FDs and self-column-map count; write result to *cache_path*.

    Runs in a subprocess so slow GT tables (wide schemas, many FDs) never block
    MCTS startup.  The internal fdtool already has a 60 s thread timeout, so 90 s
    here gives it room to finish gracefully and still write the cache file.

    Returns True if the cache was written successfully, False otherwise.
    """
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_gt_score_cache_worker,
        args=(ground_truth_location, cache_path, result_queue),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        logger.warning(
            f"[GT score cache] Timed out after {timeout}s — "
            "GT FDs will be recomputed each scoring iteration"
        )
        proc.terminate()
        proc.join()
        return False

    if not result_queue.empty():
        return bool(result_queue.get())
    return False


# ──────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
# Tree visualisation helper
# ──────────────────────────────────────────────────────────────────────────────

def _ascii_tree(root: Any, iteration: int) -> str:
    """Render the MCTS tree as a human-readable ASCII string.

    Children are sorted by total_reward descending so the most-explored
    branch appears first.  Nodes on the best-reward path are marked ★.
    Nodes that have a cached script are marked [script].
    """
    best_ids = {id(n) for n in root.best_reward_path()}

    def _node_lines(node, prefix: str, is_last: bool) -> list:
        label = node.operation_history[-1][:72] if node.operation_history else "ROOT"
        tags = ""
        if node.best_script:
            tags += " [script]"
        if id(node) in best_ids:
            tags += " ★"
        connector = "└── " if is_last else "├── "
        line = (
            prefix + connector
            + f"{label}  "
            + f"v={node.visits}  q={node.q_value:.3f}  "
            + f"Σr={node.total_reward:.3f}  score={node.best_score:.3f}"
            + tags
        )
        result = [line]
        child_prefix = prefix + ("    " if is_last else "│   ")
        children = sorted(node.children.values(), key=lambda c: c.total_reward, reverse=True)
        for i, child in enumerate(children):
            result.extend(_node_lines(child, child_prefix, i == len(children) - 1))
        return result

    root_tags = " ★" if id(root) in best_ids else ""
    header = (
        f"=== MCTS tree after iteration {iteration} ===\n"
        f"ROOT  v={root.visits}  q={root.q_value:.3f}  "
        f"Σr={root.total_reward:.3f}  score={root.best_score:.3f}{root_tags}"
    )
    children = sorted(root.children.values(), key=lambda c: c.total_reward, reverse=True)
    child_lines = []
    for i, child in enumerate(children):
        child_lines.extend(_node_lines(child, "", i == len(children) - 1))
    return header + ("\n" + "\n".join(child_lines) if child_lines else "")


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
    max_depth = getattr(args, "max_depth", 15)
    early_stopping = getattr(args, "early_stopping", 5)
    cost_budget = getattr(args, "cost_budget", 0.0)
    validation = getattr(args, "validation", "hard_match")
    reward_mode = getattr(args, "reward", "score")
    join_flag = getattr(args, "join_flag", 0)
    aggregate_flag = getattr(args, "aggregate_flag", 0)
    join_hints_truncate = getattr(args, "join_hints_truncate", [])
    aggregate_hints_truncate = getattr(args, "aggregate_hints_truncate", [])
    few_shot = getattr(args, "few_shot", 0)
    llm_judge = getattr(args, "llm_judge", "none")
    benchmark = getattr(args, "benchmark", "github")
    data_split = getattr(args, "data_split", "test")
    main_folder = (
        "autopipeline-benchmarks/monteprep-pipelines"
        if benchmark == "monteprep"
        else "autopipeline-benchmarks/github-pipelines"
    )

    # ── Case path and data file selection ──────────────────────────────────
    len_id = length
    target_id = id_

    # Create task list based on id range (file_count will be calculated per task)
    task_list = [f"length{length}_{i}" for i in range(id_, id_ + 1)]

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

        # ── Calculate file_count for THIS task and select appropriate JSON ────
        path_to_files = f"{main_folder}/{task}/"
        file_count = sum(
            1
            for file in os.listdir(path_to_files)
            if file.startswith(data_split) and os.path.isfile(os.path.join(path_to_files, file))
        )
        if benchmark == "monteprep":
            json_file_path = "data/chatgpt_monteprep_ms.json" if file_count > 1 else "data/chatgpt_monteprep_ss.json"
        else:
            json_file_path = "data/chatgpt_github_ms.json" if file_count > 1 else "data/chatgpt_github_ss.json"

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
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag, data_split=data_split)

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger, cost_budget=cost_budget)

        target_file_location = (
            f"{main_folder}/length{len_idx_target_idx}/target_multisource_mcts.csv"
        )
        ground_truth_location = f"{main_folder}/length{len_idx_target_idx}/target.csv"

        # ── Pre-compute GT scoring cache (FDs + self-col-map) — done once per case ──
        _gt_score_cache_path = f"/tmp/gt_score_cache_{len_idx_target_idx}.json"
        _gt_cache_ok = _compute_gt_score_cache(
            ground_truth_location=ground_truth_location,
            cache_path=_gt_score_cache_path,
            logger=logger,
            timeout=90,
        )
        if _gt_cache_ok:
            logger.info(f"[GT score cache] Pre-computed → {_gt_score_cache_path}")
        else:
            _gt_score_cache_path = ""

        # ── Intermediate materialization setup ────────────────────────────────
        intermediate_materialization = getattr(args, "intermediate_materialization", False)
        interm_space_dir = None
        if intermediate_materialization:
            from methods.multi_step import create_intermediate_space
            interm_space_dir = create_intermediate_space(main_folder, len_id, target_id)
        config_directory = interm_space_dir if intermediate_materialization else main_folder

        # ── Critique support: pre-compute source_information and fd_hints ────
        mcts_critique_mode = getattr(args, "mcts_critique_mode", "none")
        try:
            if model == "gpt-4.1-mini":
                _enc = tiktoken.get_encoding("o200k_base")
            elif model in ("o4-mini", "o3"):
                _enc = tiktoken.get_encoding("cl100k_base")
            else:
                _enc = tiktoken.encoding_for_model(model)
        except Exception:
            _enc = tiktoken.get_encoding("cl100k_base")

        source_information = get_source(
            file_count, source_data_name_list, source_data_schema_list,
            main_folder, len_idx_target_idx, source_length, token_limit, _enc,
            data_split=data_split,
        )

        fd_hints_str = ""
        if fd_flag:
            try:
                df_gt_fd = pd.read_csv(ground_truth_location, low_memory=False)
                df_gt_fd = df_gt_fd.drop(columns=df_gt_fd.columns[0], axis=1)
                df_gt_fd = df_gt_fd.sample(
                    n=min(1000, df_gt_fd.shape[0]), replace=False
                ).iloc[:, :15]
                key, fd__ = get_filtered_functional_dependency(df_gt_fd)
                fd_hints_str = "Keys : " + str(key) + "\nFunctional Dependencies : " + str(fd__)
            except Exception:
                pass

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
            directory=config_directory,
            source_information=source_information,
            static_hints=not getattr(args, "no_static_hints", False),
            fd_hints=fd_hints_str,
            mcts_critique_mode=mcts_critique_mode,
            reward_mode=reward_mode,
            intermediate_materialization=intermediate_materialization,
            data_split=data_split,
        )

        # ── Heuristic GROUP BY candidates (computed once, cached in config) ────
        # Both run regardless of fd_flag / hint_source.  Hard timeouts prevent
        # slow tables from eating into the MCTS iteration budget.

        # FD-based: keys from target table functional-dependency analysis (60 s)
        config.hint_groupby_fd_candidate = _compute_fd_groupby_candidate(
            target_file=ground_truth_location,
            source_name_list=source_data_name_list,
            source_schema_list=source_data_schema_list,
            logger=logger,
            timeout=60,
        )

        # hints_v3-based: statistical column checks on source tables (30 s)
        config.hint_groupby_v3_candidate = _compute_hints_v3_groupby_candidate(
            source_name_list=source_data_name_list,
            directory=config_directory,
            len_idx_target_idx=len_idx_target_idx,
            logger=logger,
            timeout=30,
        )

        # ── Auto-build upper-bound RAG DB from ground-truth CSV ──────────
        _rag_mode = getattr(args, "rag", "")
        _local_rag_db = getattr(args, "local_rag_db", "")
        if _rag_mode == "upper_bound" and not _local_rag_db:
            _gt_csv = getattr(args, "gt_csv", "ground_truth_pipelines.csv")
            _auto_db_path = f"/tmp/rag_upper_bound_{len_idx_target_idx}.db"
            _case_folder = os.path.join(main_folder, f"length{len_idx_target_idx}")
            _ok = build_upper_bound_db(
                case_id=len_idx_target_idx,
                case_folder=_case_folder,
                gt_csv_path=_gt_csv,
                db_path=_auto_db_path,
            )
            if _ok:
                logger.info(
                    f"[RAG] upper_bound DB built at {_auto_db_path} "
                    f"for case {len_idx_target_idx}"
                )
                _local_rag_db = _auto_db_path
            else:
                logger.warning(
                    f"[RAG] upper_bound: case {len_idx_target_idx} not found in "
                    f"ground_truth_pipelines.csv — RAG disabled for this case."
                )

        # ── Global schema-embedding RAG: retrieve top-50 → populate local DB ─
        if _rag_mode == "global":
            _global_db_path = getattr(args, "global_rag_db", "")
            if not _global_db_path:
                logger.warning("[RAG] --rag global requires --global_rag_db — RAG disabled.")
            else:
                try:
                    from rag_pipeline.global_rag_db import GlobalSchemaDB
                    # model_id auto-read from <db>.meta.json written at ingestion time;
                    # --global_rag_model overrides only if explicitly passed
                    _explicit_model = getattr(args, "global_rag_model", "") or None
                    _gdb = GlobalSchemaDB(
                        db_path=_global_db_path,
                        model_id=_explicit_model,
                        device=getattr(args, "global_rag_device", "auto"),
                    )
                    logger.info(f"[RAG] global: using embedding model {_gdb._model_id}")
                    _global_top_k = getattr(args, "global_rag_top_k", 50)
                    logger.info(
                        f"[RAG] global: querying top {_global_top_k} from {_global_db_path} "
                        f"for case {len_idx_target_idx}"
                    )
                    _rag_search_t0 = time.time()
                    _global_results = _gdb.search(
                        target_schema=config.target_data_schema,
                        source_schemas=config.source_data_schema_list,
                        top_k=_global_top_k,
                    )
                    _rag_search_sec = time.time() - _rag_search_t0
                    logger.info(
                        f"[RAG] global: retrieved {len(_global_results)} candidates "
                        f"in {_rag_search_sec:.2f}s"
                    )
                    _auto_db_path = f"/tmp/rag_global_{len_idx_target_idx}_k{_global_top_k}.db"
                    _rag_populate_t0 = time.time()
                    _n_inserted = populate_from_global_results(_auto_db_path, _global_results)
                    _rag_populate_sec = time.time() - _rag_populate_t0
                    logger.info(
                        f"[RAG] global: populated local SQLite with {_n_inserted} examples "
                        f"in {_rag_populate_sec:.2f}s at {_auto_db_path}"
                    )
                    _local_rag_db = _auto_db_path
                except Exception:
                    import traceback as _tb
                    logger.warning(
                        f"[RAG] global retrieval failed — RAG disabled for this case.\n"
                        f"{_tb.format_exc()}"
                    )

        # ── Global feature-vector RAG: retrieve top-k → populate local DB ────
        if _rag_mode == "global_feature":
            _feature_db_path = getattr(args, "global_feature_rag_db", "")
            if not _feature_db_path:
                logger.warning(
                    "[RAG] --rag global_feature requires --global_feature_rag_db — RAG disabled."
                )
            else:
                try:
                    from pathlib import Path as _Path
                    from rag_pipeline.global_rag_db import GlobalFeatureDB
                    from rag_pipeline.feature_extractor import load_source_target_from_folder
                    _fdb = GlobalFeatureDB(db_path=_feature_db_path)
                    logger.info(
                        f"[RAG] global_feature: {_fdb.count()} indexed cases "
                        f"from {_feature_db_path}"
                    )
                    _global_top_k = getattr(args, "global_rag_top_k", 50)
                    _task_folder = _Path(main_folder) / f"length{len_idx_target_idx}"
                    _source_dfs, _target_df = load_source_target_from_folder(_task_folder)
                    logger.info(
                        f"[RAG] global_feature: querying top {_global_top_k} "
                        f"for case {len_idx_target_idx}"
                    )
                    _rag_search_t0 = time.time()
                    _global_results = _fdb.search(
                        source_dfs=_source_dfs,
                        target_df=_target_df,
                        top_k=_global_top_k,
                        exclude_case_id=len_idx_target_idx,
                    )
                    _rag_search_sec = time.time() - _rag_search_t0
                    logger.info(
                        f"[RAG] global_feature: retrieved {len(_global_results)} candidates "
                        f"in {_rag_search_sec:.2f}s"
                    )
                    _auto_db_path = f"/tmp/rag_global_feature_{len_idx_target_idx}_k{_global_top_k}.db"
                    _rag_populate_t0 = time.time()
                    _n_inserted = populate_from_global_results(_auto_db_path, _global_results)
                    _rag_populate_sec = time.time() - _rag_populate_t0
                    logger.info(
                        f"[RAG] global_feature: populated local SQLite with {_n_inserted} "
                        f"examples in {_rag_populate_sec:.2f}s at {_auto_db_path}"
                    )
                    _local_rag_db = _auto_db_path
                except Exception:
                    import traceback as _tb
                    logger.warning(
                        f"[RAG] global_feature retrieval failed — RAG disabled for this case.\n"
                        f"{_tb.format_exc()}"
                    )

        # ── Build initial MCTS state ──────────────────────────────────────
        root = MCTSNode(operation_history=[], parent=None, operator_type=None)

        initial_state: MCTSGraphState = {
            # Problem config
            "config": config,
            "main_folder": main_folder,
            "ground_truth_location": ground_truth_location,
            "target_file_location": target_file_location,
            "validation_mode": validation,
            "reward_mode": reward_mode,
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
            "max_depth": max_depth,
            "early_stopping": early_stopping,
            "cost_budget": cost_budget,
            "cost_budget_exhausted": False,
            "terminal_found": False,
            "validation_passed": False,
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
            "no_improvement_count": 0,
            "latest_script": "",
            # Critique
            "simulation_mode": getattr(args, "simulation_mode", "pipeline"),
            "intermediate_materialization": intermediate_materialization,
            "llm_judge": llm_judge,
            "judge_verdict": False,
            "critique_attempted": False,
            "pre_critique_score": 0.0,
            "critique_selection_path": [],
            "critique_score": 0.0,
            # Stopping criteria
            "no_score_threshold": getattr(args, "no_score_threshold", False),
            # RAG support — active for upper_bound and global modes
            "local_rag_db_path": _local_rag_db if _rag_mode in ("upper_bound", "global", "global_feature") else "",
            # GT scoring cache — pre-computed FDs and self-col-map to skip per-iteration recomputation
            "gt_score_cache_path": _gt_score_cache_path,
            # Logging
            "log_messages": [],
        }

        # ── Run MCTS graph ────────────────────────────────────────────────
        logger.info(
            f"[MCTS] Starting search: max_iterations={max_iterations}, "
            f"case={len_idx_target_idx}"
        )
        mcts_graph = build_mcts_graph()
        _checkpoint_file = f"/tmp/mcts_checkpoint_{len_idx_target_idx}.json"
        final_state: MCTSGraphState = initial_state
        # Cost-budget mode can run far more iterations — raise the graph step limit accordingly
        _recursion_limit = 10000 if cost_budget > 0.0 else 500
        _prev_iter = 0  # track completed iterations for per-iteration tree files
        for _step_state in mcts_graph.stream(
            initial_state,
            config={"recursion_limit": _recursion_limit},
            stream_mode="values",
        ):
            final_state = _step_state

            # Overwrite tree_latest.txt whenever a new iteration completes
            # (backpropagate increments state["iteration"]).
            _curr_iter = _step_state.get("iteration", 0)
            if _curr_iter > _prev_iter:
                _snap_root = _step_state.get("root")
                if _snap_root is not None:
                    _tree_out = os.path.join(log_dir_, "tree_latest.txt")
                    try:
                        with open(_tree_out, "w") as _tf:
                            _tf.write(_ascii_tree(_snap_root, _prev_iter))
                    except Exception:
                        pass
                _prev_iter = _curr_iter

            # Checkpoint the best-reward-path leaf script after every graph step so
            # timeout/OOM recovery uses the same path-based selection as extract_best.
            try:
                _ckpt_root = _step_state.get("root")
                if _ckpt_root is not None and _ckpt_root.visits > 0:
                    _ckpt_leaf = _ckpt_root.best_reward_path()[-1]
                    _ckpt_script = _ckpt_leaf.best_script
                    _ckpt_score = _ckpt_leaf.best_score
                    _ckpt_history = str(_ckpt_leaf.operation_history)
                else:
                    _ckpt_script = _step_state.get("best_script") or _step_state.get("latest_script", "")
                    _ckpt_score = _step_state.get("best_score", 0.0)
                    _ckpt_history = str(_step_state.get("best_operation_history", []))
                if _ckpt_script:
                    with open(_checkpoint_file, "w") as _cf:
                        json.dump({
                            "best_script": _ckpt_script,
                            "best_score": _ckpt_score,
                            "best_operation_history": _ckpt_history,
                        }, _cf)
            except Exception:
                pass

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
            # Re-execute best script so target_file_location reflects the best result,
            # then validate. Only reached when MCTS never found a validated result.
            try:
                from util.utils import execute_python
                exec_result = execute_python(best_script)
                if exec_result != "Success":
                    logger.warning(f"[MCTS] best_script execution failed: {exec_result}")
            except Exception:
                logger.warning(
                    f"[MCTS] best_script execution raised: {traceback.format_exc()}"
                )

            try:
                validate_fn = (
                    compare_tables_matching
                    if validation == "autopipeline"
                    else compare_lists_matching
                )
                df_output = pd.read_csv(target_file_location, low_memory=False)
                df_gt = pd.read_csv(ground_truth_location, low_memory=False)
                df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
                _, is_correct, _, _ = validate_fn(df_output, df_gt)
            except Exception:
                logger.warning(
                    f"[MCTS] Hard accuracy eval failed: {traceback.format_exc()}"
                )
                is_correct = False

        # ── Two-phase validation: final is_correct on test data ───────────────
        if data_split == "training" and best_script:
            test_script = make_test_validation_script(best_script)
            test_output = f"{main_folder}/length{len_idx_target_idx}/target_multisource_mcts_test_val.csv"
            print("[two-phase mcts] executing test-data script for final is_correct...")
            try:
                from util.utils import execute_python as _exec_py
                test_exec = _exec_py(test_script)
            except Exception:
                test_exec = f"Error: {traceback.format_exc()}"
            if test_exec == "Success" and os.path.exists(test_output):
                try:
                    df_test = pd.read_csv(test_output, low_memory=False)
                    df_gt_test = pd.read_csv(ground_truth_location, low_memory=False)
                    df_gt_test = df_gt_test.drop(columns=df_gt_test.columns[0], axis=1)
                    _, test_is_correct, _, _ = validate_fn(df_test, df_gt_test)
                    print(f"[two-phase mcts] is_correct: training={is_correct} → test={test_is_correct}")
                    is_correct = test_is_correct
                except Exception:
                    print(f"[two-phase mcts] test validation failed:\n{traceback.format_exc()}")
            else:
                print(f"[two-phase mcts] test exec={test_exec}, output_exists={os.path.exists(test_output)}")

        try:
            os.remove(_checkpoint_file)
        except OSError:
            pass

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

def _case_worker(args, length, case_id, log_dir_, experiment_name, result_queue):
    """Worker function run in a child process for each case."""
    try:
        result = mcts_search(
            args, length=length, id_=case_id,
            log_dir_=log_dir_, experiment_name=experiment_name, i_=case_id,
        )
        result_queue.put(("ok", result))
    except Exception:
        result_queue.put(("error", traceback.format_exc()))


if __name__ == "__main__":
    import argparse
    import csv
    import multiprocessing
    from datetime import datetime

    _CASE_TIMEOUT = 300  # 5 minutes per case

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
    parser.add_argument("--mcts_iterations", type=int, default=5)
    parser.add_argument(
        "--max_depth",
        type=int,
        default=15,
        help=(
            "Hard cap on tree depth (default: 15). Nodes at this depth are treated as forced leaves: "
            "they are simulated once and their cached reward is reused on subsequent selections. "
            "They never spawn children regardless of how many iterations remain."
        ),
    )
    parser.add_argument(
        "--no_score_threshold",
        action="store_true",
        default=False,
        help=(
            "Suppress score-based early stopping for 'score' and 'det_score_value' reward modes. "
            "The search runs to its full iteration/cost budget and returns the best-scoring script. "
            "Useful for re-running failed cases without the 0.9 threshold stopping the search early."
        ),
    )
    parser.add_argument("--early_stopping", type=int, default=5,
                        help="Stop if best_score does not improve for this many consecutive iterations (default: 5); "
                             "set to 0 to disable plateau stopping in cost-budget mode")
    parser.add_argument(
        "--cost_budget",
        type=float,
        default=0.0,
        help=(
            "Max USD to spend per case (e.g. 0.05 = 5 cents). "
            "When >0, switches to cost-budget mode: iteration cap is ignored and cost is the primary "
            "stopping criterion. Set --early_stopping 0 to also disable the score-plateau check."
        ),
    )
    parser.add_argument("--join_flag", type=int, default=0)
    parser.add_argument("--aggregate_flag", type=int, default=0)
    parser.add_argument("--few_shot", type=int, default=0)
    parser.add_argument(
        "--mcts_critique_mode",
        type=str,
        default="none",
        choices=["none", "simulate", "best"],
        help="Critique mode: 'none'=disabled, 'simulate'=after each iteration when score<1.0, 'best'=once on final best script",
    )
    parser.add_argument(
        "--no_static_hints",
        action="store_true",
        default=False,
        help="Suppress static hints (CRITIQUE_HINT_IDS) from the critique prompt (hints are on by default)",
    )
    parser.add_argument(
        "--validation",
        type=str,
        default="hard_match",
        choices=["hard_match", "autopipeline"],
        help="Validation method: 'hard_match' uses compare_lists_matching (partial credit), 'autopipeline' uses compare_tables_matching (binary match)",
    )
    parser.add_argument(
        "--reward",
        type=str,
        default="score",
        choices=["score", "det_score_value", "validation", "partial"],
        help=(
            "MCTS reward signal used for backpropagation: "
            "'score' = continuous relative_csv_score (FD + column map + distribution), "
            "'det_score_value' = value_based_relative_csv_score (Jaccard-aligned columns + value-based distribution), "
            "'validation' = binary 1.0 if hard-match validation passes else 0.0, "
            "'partial' = fuzzy column-match ratio (matched target cols / total target cols)"
        ),
    )
    parser.add_argument(
        "--simulation",
        type=str,
        default="pipeline",
        choices=["pipeline", "operator"],
        dest="simulation_mode",
        help=(
            "Simulation strategy: 'pipeline' = one LLM call completes the full script "
            "(default); 'operator' = multistep operator-by-operator simulation using "
            "get_next_operator + configure prompts, then python_script."
        ),
    )
    parser.add_argument(
        "--intermediate_materialization",
        action="store_true",
        default=False,
        help=(
            "Materialize and score the intermediate table after each operator step "
            "(operator simulation mode only). Mirrors --intermediate_materialization "
            "from critique_data.py."
        ),
    )
    parser.add_argument(
        "--llm_judge",
        type=str,
        default="none",
        choices=["none", "det_score", "llm", "llm_score", "llm_score_hybrid"],
        help=(
            "LLM judge used as stopping criterion: "
            "'none'=disabled (score/validation-based stopping), "
            "'det_score'=deterministic score threshold, "
            "'llm'=LLM table comparison, "
            "'llm_score'=LLM + numeric score, "
            "'llm_score_hybrid'=LLM + NL score interpretation."
        ),
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="github",
        choices=["github", "monteprep"],
        help="Benchmark dataset: 'github' or 'monteprep'.",
    )
    parser.add_argument(
        "--data_split",
        type=str,
        default="test",
        choices=["test", "training"],
        help="Which CSV split to use as source examples: 'test' (default) or 'training'.",
    )
    parser.add_argument(
        "--result_dir",
        type=str,
        default="results_langraph",
        help="Base directory for results (a timestamped subdirectory is created inside)",
    )
    parser.add_argument(
        "--log_dir",
        type=str,
        default="",
        help="Override per-case log directory (default: logs_langraph/{experiment_name})",
    )
    parser.add_argument(
        "--cases",
        type=str,
        nargs="+",
        default=None,
        help="Explicit list of case IDs to run, e.g. --cases 1_41 4_18 9_70. "
             "Overrides --length / --id_start / --id_end.",
    )
    parser.add_argument(
        "--local_rag_db",
        type=str,
        default="",
        help=(
            "Path to a pre-built per-case SQLite RAG database "
            "(created by rag_pipeline/local_rag_db.py).  "
            "Required when --rag upper_bound is set."
        ),
    )
    parser.add_argument(
        "--gt_csv",
        type=str,
        default="ground_truth_pipelines.csv",
        help="Path to ground_truth_pipelines.csv used to build the upper-bound RAG DB.",
    )
    parser.add_argument(
        "--rag",
        type=str,
        default="",
        choices=["upper_bound", "global", "global_feature"],
        help=(
            "Enable RAG-augmented prompts.  "
            "'upper_bound' injects hints from a pre-built local SQLite DB "
            "(supply the path via --local_rag_db).  "
            "'global' uses schema-embedding retrieval (supply --global_rag_db).  "
            "'global_feature' uses 22-dim structural feature retrieval "
            "(supply --global_feature_rag_db).  "
            "Omit to disable RAG entirely."
        ),
    )
    parser.add_argument(
        "--global_rag_db",
        type=str,
        default="",
        help=(
            "Path to the global Milvus schema DB built by "
            "rag_pipeline/ingest_global_db.py.  Required when --rag global."
        ),
    )
    parser.add_argument(
        "--global_rag_top_k",
        type=int,
        default=50,
        help="Number of candidates to retrieve from the global DB (default: 50).",
    )
    parser.add_argument(
        "--global_rag_model",
        type=str,
        default="",
        help=(
            "Embedding model for the global schema DB. "
            "Auto-read from <db>.meta.json written at ingestion time — "
            "only pass this to override."
        ),
    )
    parser.add_argument(
        "--global_rag_device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu", "mps"],
        help="Device for the global RAG embedding model (default: auto).",
    )
    parser.add_argument(
        "--global_feature_rag_db",
        type=str,
        default="",
        help=(
            "Path prefix for the GlobalFeatureDB built by "
            "rag_pipeline/ingest_global_feature_db.py "
            "(e.g. rag_pipeline/db/global_features). "
            "Required when --rag global_feature."
        ),
    )
    args = parser.parse_args()
    args.join_hints_truncate = []
    args.aggregate_hints_truncate = []

    # Change to project root so relative imports work
    os.chdir(_ROOT)

    # All logs for this run go under a single experiment directory
    log_dir_ = args.log_dir if args.log_dir else os.path.join("logs_langraph", args.experiment_name)
    os.makedirs(log_dir_, exist_ok=True)

    # Results directory and CSV
    _run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(
        _HERE, args.result_dir, f"{args.experiment_name}_{_run_timestamp}"
    )
    os.makedirs(results_dir, exist_ok=True)
    results_csv_path = os.path.join(results_dir, "results_summary.csv")

    _CSV_FIELDS = [
        "case_id",
        "is_correct",
        "cost",
        "latency_seconds",
        "best_score",
        "operation_history",
        "timestamp",
        "status",
        "error",
    ]
    with open(results_csv_path, "w", newline="") as _f:
        csv.DictWriter(_f, fieldnames=_CSV_FIELDS).writeheader()

    print(f"[MCTS] Results will be written to: {results_csv_path}")

    # Build case list: explicit --cases overrides --length / --id_start / --id_end
    if args.cases:
        case_pairs = [(int(c.split("_")[0]), int(c.split("_")[1])) for c in args.cases]
    else:
        case_pairs = [(args.length, cid) for cid in range(args.id_start, args.id_end + 1)]

    results = {}
    for length, case_id in case_pairs:
        print(f"\n[MCTS] === length={length}  id={case_id} ===")
        case_label = f"{length}_{case_id}"
        _ts = datetime.now().isoformat()
        _result_queue = multiprocessing.Queue()
        _proc = multiprocessing.Process(
            target=_case_worker,
            args=(args, length, case_id, log_dir_, args.experiment_name, _result_queue),
        )
        _proc.start()
        _proc.join(timeout=_CASE_TIMEOUT)

        if _proc.is_alive():
            print(f"[MCTS] Case {case_id} TIMED OUT after {_CASE_TIMEOUT}s — killing")
            _proc.terminate()
            _proc.join()
            results[case_id] = None

            # Attempt to recover the best script written during the run
            _checkpoint_file = f"/tmp/mcts_checkpoint_{length}_{case_id}.json"
            _recovered = False
            if os.path.exists(_checkpoint_file):
                try:
                    with open(_checkpoint_file) as _cf:
                        _ckpt = json.load(_cf)
                    _best_script = _ckpt.get("best_script", "")
                    _best_score = _ckpt.get("best_score", 0.0)
                    _best_op_hist = _ckpt.get("best_operation_history", "")
                    if _best_script:
                        _mf = (
                            "autopipeline-benchmarks/monteprep-pipelines"
                            if args.benchmark == "monteprep"
                            else "autopipeline-benchmarks/github-pipelines"
                        )
                        _target_file = f"{_mf}/length{length}_{case_id}/target_multisource_mcts.csv"
                        _gt_file = f"{_mf}/length{length}_{case_id}/target.csv"
                        from util.utils import execute_python
                        _exec_result = execute_python(_best_script)
                        _validate_fn = (
                            compare_tables_matching
                            if args.validation == "autopipeline"
                            else compare_lists_matching
                        )
                        _data_split = getattr(args, "data_split", "test")
                        if _exec_result == "Success":
                            _df_out = pd.read_csv(_target_file, low_memory=False)
                            _df_gt = pd.read_csv(_gt_file, low_memory=False)
                            _df_gt = _df_gt.drop(columns=_df_gt.columns[0], axis=1)
                            _, _is_correct, _, _ = _validate_fn(_df_out, _df_gt)
                            # Two-phase: override is_correct with test-data validation.
                            # Use a recovery-specific output path to avoid race conditions
                            # with any orphaned test-validation subprocess still writing to
                            # the shared target_multisource_mcts_test_val.csv path.
                            if _data_split == "training":
                                _test_file = f"{_mf}/length{length}_{case_id}/target_multisource_mcts_recovery_test_val.csv"
                                _test_script_raw = make_test_validation_script(_best_script)
                                _test_script = _test_script_raw.replace(
                                    "target_multisource_mcts_test_val.csv",
                                    "target_multisource_mcts_recovery_test_val.csv"
                                )
                                _case_log_dir = os.path.join(log_dir_, f"cases_c{case_id}")
                                os.makedirs(_case_log_dir, exist_ok=True)
                                # Save the test script for inspection
                                _saved_script = os.path.join(_case_log_dir, "recovery_test_script.py")
                                with open(_saved_script, "w") as _sf:
                                    _sf.write(_test_script)
                                _test_exec = execute_python(_test_script)
                                if _test_exec == "Success" and os.path.exists(_test_file):
                                    try:
                                        _df_test = pd.read_csv(_test_file, low_memory=False)
                                        _df_gt2 = pd.read_csv(_gt_file, low_memory=False)
                                        _df_gt2 = _df_gt2.drop(columns=_df_gt2.columns[0], axis=1)
                                        _, _test_is_correct, _, _ = _validate_fn(_df_test, _df_gt2)
                                        print(f"[two-phase mcts timeout] is_correct: training={_is_correct} → test={_test_is_correct}")
                                        _is_correct = _test_is_correct
                                    except Exception:
                                        print(f"[two-phase mcts timeout] test validation failed")
                                    finally:
                                        if os.path.exists(_test_file):
                                            os.remove(_test_file)
                            _recovered = True
                            print(
                                f"[MCTS] Case {case_id} timeout-recovered: "
                                f"is_correct={_is_correct}, best_score={_best_score:.4f}"
                            )
                            _row = {
                                "case_id": case_label,
                                "is_correct": _is_correct,
                                "cost": "N/A",
                                "latency_seconds": _CASE_TIMEOUT,
                                "best_score": round(_best_score, 4),
                                "operation_history": _best_op_hist,
                                "timestamp": _ts,
                                "status": "timeout_recovered",
                                "error": f"Timed out after {_CASE_TIMEOUT}s; best script validated",
                            }
                    os.remove(_checkpoint_file)
                except Exception as _e:
                    print(f"[MCTS] Case {case_id} timeout recovery failed: {_e}")

            if not _recovered:
                _row = {
                    "case_id": case_label,
                    "is_correct": False,
                    "cost": "N/A",
                    "latency_seconds": _CASE_TIMEOUT,
                    "best_score": "N/A",
                    "operation_history": "",
                    "timestamp": _ts,
                    "status": "timeout",
                    "error": f"Timed out after {_CASE_TIMEOUT}s",
                }
        elif not _result_queue.empty():
            _status, _payload = _result_queue.get()
            if _status == "ok":
                result = _payload
                results[case_id] = result
                is_correct, total_cost, time_elapsed, best_score, op_hist_ = result
                print(f"[MCTS] Case {case_id} done: {result}")
                _row = {
                    "case_id": case_label,
                    "is_correct": is_correct,
                    "cost": round(total_cost, 6) if total_cost is not None else "N/A",
                    "latency_seconds": round(time_elapsed, 2),
                    "best_score": round(best_score, 4),
                    "operation_history": op_hist_,
                    "timestamp": _ts,
                    "status": "correct" if is_correct else "incorrect",
                    "error": "",
                }
            else:
                tb = _payload
                print(f"[MCTS] Case {case_id} FAILED:\n{tb}")
                results[case_id] = None
                _row = {
                    "case_id": case_label,
                    "is_correct": False,
                    "cost": "N/A",
                    "latency_seconds": "N/A",
                    "best_score": "N/A",
                    "operation_history": "",
                    "timestamp": _ts,
                    "status": "error",
                    "error": tb.strip().splitlines()[-1],
                }
        else:
            _exitcode = _proc.exitcode
            print(f"[MCTS] Case {case_id} exited with no result (exit code {_exitcode})")
            results[case_id] = None

            # Attempt checkpoint recovery (same logic as timeout path) —
            # covers OOM kills (-9) and other unexpected exits where the
            # subprocess wrote at least one checkpoint during iteration.
            _checkpoint_file = f"/tmp/mcts_checkpoint_{length}_{case_id}.json"
            _recovered = False
            if os.path.exists(_checkpoint_file):
                try:
                    with open(_checkpoint_file) as _cf:
                        _ckpt = json.load(_cf)
                    _best_script = _ckpt.get("best_script", "")
                    _best_score  = _ckpt.get("best_score", 0.0)
                    _best_op_hist = _ckpt.get("best_operation_history", "")
                    if _best_script:
                        _mf = (
                            "autopipeline-benchmarks/monteprep-pipelines"
                            if args.benchmark == "monteprep"
                            else "autopipeline-benchmarks/github-pipelines"
                        )
                        _target_file = f"{_mf}/length{length}_{case_id}/target_multisource_mcts.csv"
                        _gt_file = f"{_mf}/length{length}_{case_id}/target.csv"
                        from util.utils import execute_python
                        _exec_result = execute_python(_best_script)
                        _validate_fn = (
                            compare_tables_matching
                            if args.validation == "autopipeline"
                            else compare_lists_matching
                        )
                        _data_split = getattr(args, "data_split", "test")
                        if _exec_result == "Success":
                            _df_out = pd.read_csv(_target_file, low_memory=False)
                            _df_gt  = pd.read_csv(_gt_file, low_memory=False)
                            _df_gt  = _df_gt.drop(columns=_df_gt.columns[0], axis=1)
                            _, _is_correct, _, _ = _validate_fn(_df_out, _df_gt)
                            if _data_split == "training":
                                _test_file = f"{_mf}/length{length}_{case_id}/target_multisource_mcts_recovery_test_val.csv"
                                _test_script_raw = make_test_validation_script(_best_script)
                                _test_script = _test_script_raw.replace(
                                    "target_multisource_mcts_test_val.csv",
                                    "target_multisource_mcts_recovery_test_val.csv"
                                )
                                _case_log_dir = os.path.join(log_dir_, f"cases_c{case_id}")
                                os.makedirs(_case_log_dir, exist_ok=True)
                                # Save the test script for inspection
                                _saved_script = os.path.join(_case_log_dir, "recovery_test_script.py")
                                with open(_saved_script, "w") as _sf:
                                    _sf.write(_test_script)
                                _test_exec = execute_python(_test_script)
                                if _test_exec == "Success" and os.path.exists(_test_file):
                                    try:
                                        _df_test = pd.read_csv(_test_file, low_memory=False)
                                        _df_gt2  = pd.read_csv(_gt_file, low_memory=False)
                                        _df_gt2  = _df_gt2.drop(columns=_df_gt2.columns[0], axis=1)
                                        _, _test_is_correct, _, _ = _validate_fn(_df_test, _df_gt2)
                                        print(f"[two-phase mcts oom] is_correct: training={_is_correct} → test={_test_is_correct}")
                                        _is_correct = _test_is_correct
                                    except Exception:
                                        print(f"[two-phase mcts oom] test validation failed")
                                    finally:
                                        if os.path.exists(_test_file):
                                            os.remove(_test_file)
                            _recovered = True
                            print(
                                f"[MCTS] Case {case_id} oom-recovered: "
                                f"is_correct={_is_correct}, best_score={_best_score:.4f}"
                            )
                            _row = {
                                "case_id": case_label,
                                "is_correct": _is_correct,
                                "cost": "N/A",
                                "latency_seconds": "N/A",
                                "best_score": round(_best_score, 4),
                                "operation_history": _best_op_hist,
                                "timestamp": _ts,
                                "status": "oom_recovered",
                                "error": f"Process killed (code {_exitcode}); best script validated",
                            }
                    os.remove(_checkpoint_file)
                except Exception as _e:
                    print(f"[MCTS] Case {case_id} oom recovery failed: {_e}")

            if not _recovered:
                _row = {
                    "case_id": case_label,
                    "is_correct": False,
                    "cost": "N/A",
                    "latency_seconds": "N/A",
                    "best_score": "N/A",
                    "operation_history": "",
                    "timestamp": _ts,
                    "status": "error",
                    "error": f"Process exited with code {_exitcode}",
                }
        with open(results_csv_path, "a", newline="") as _f:
            csv.DictWriter(_f, fieldnames=_CSV_FIELDS).writerow(_row)
        print(f"[MCTS] CSV updated: {results_csv_path}")

    print("\n[MCTS] === Summary ===")
    for case_id, result in results.items():
        print(f"  id={case_id}: {result}")
    print(f"\n[MCTS] Results CSV: {results_csv_path}")
