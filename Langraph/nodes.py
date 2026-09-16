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
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

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
import hints.hint_v3 as hint_v3

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
    POST_AGGREGATE_EXPAND_OPS,
)
from state import MCTSGraphState
from util.utils import execute_python, drop_leading_index_col_if_present
from validation.hard_match import compare_lists_matching, compare_tables_matching
from validation.fuzzy_match import compare_tables_fuzzy

# Maximum tree selection depth (used in mcts_select only)
_MAX_SELECT_DEPTH = 15
# Maximum code-generation retries inside simulate
_MAX_CODE_TRIALS = 5
# Maximum operator steps in one operator-level simulation rollout
_MAX_SIMULATE_STEPS = 15
# Hard timeout (seconds) for the full scoring + validation call.
# relative_csv_score() now does its own two-phase FD mining per side (full
# table, then a truncated retry if that times out), each phase capped at
# eval_score/score.py's FD_TIMEOUT (30s) -- so one side can take up to 60s
# worst case, and a call needing fresh FD mining on both the generated output
# and the ground truth (GT cache unavailable) can take up to 120s. Sized to
# cover that plus subprocess spawn/communication overhead.
_SCORE_TIMEOUT = 2 * (2 * 30) + 20


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
        df_gt = drop_leading_index_col_if_present(df_gt)

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
        # relative_csv_score() spawns its own child process for FD mining
        # (eval_score/score.py's _run_fdtool) -- a daemonic process can't have
        # children, so this parent must not be daemonic either.
        daemon=False,
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


def _value_score_worker(target_file_location: str, ground_truth_location: str, result_queue,
                        gt_cache_path: str = "", weights: dict | None = None,
                        confidence: float | None = None, column_type_weights: dict | None = None,
                        credibility_weight: float | None = None):
    """Subprocess worker: load CSVs and compute value_based score, put result in queue.

    Uses Jaccard-aligned column matching + value-based distribution scoring.
    If the cache recorded GT was reduced (col_indices set), both df_gt and
    df_output are truncated to the same columns/rows before scoring. FD-mining
    timeouts are handled internally by relative_csv_score() (two-phase: full
    table, then a truncated retry), so no outer truncate-and-retry is needed
    here -- a timeout of the whole worker process is treated as a genuine
    failure, not a signal to retry smaller.

    weights: optional score_1 component weights (fd_f1/avg_col_score_1/
        row_count_score/max_missing_score/confidence/credibility_weight),
        forwarded to value_based_relative_csv_score. Defaults to equal
        weights there.
    confidence: optional self-reported LLM confidence (0.0-1.0), forwarded to
        value_based_relative_csv_score as the 5th score_1 component. None
        (default) excludes it, reproducing the original 4-component score_1.
    column_type_weights: optional per-column-type (float/int/id/cat) sub-metric
        weights, forwarded to value_based_relative_csv_score. None reproduces
        the original hardcoded per-type formulas.
    credibility_weight: optional pipeline-frequency-based credibility signal
        (0.0-1.0), forwarded to value_based_relative_csv_score as the 6th
        score_1 component. None (default) excludes it.
    Puts a dict {"score": float, "components": {...} | None} in result_queue
    -- components are the raw (unweighted) score_1 inputs, logged
    regardless of which weights produced the score, so the score can be
    recomputed under different weights later without rerunning MCTS.
    """
    try:
        df_output = pd.read_csv(target_file_location, low_memory=False)
        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
        df_gt = drop_leading_index_col_if_present(df_gt)

        precomputed_gt = None

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

        _, _, _, fd_f1, true_combined_score, debug_dict = value_based_relative_csv_score(
            df_output, df_gt, precomputed_gt=precomputed_gt, weights=weights, confidence=confidence,
            column_type_weights=column_type_weights, credibility_weight=credibility_weight,
        )
        components = {
            "fd_f1": fd_f1,
            "avg_col_score_1": debug_dict.get("avg_col_score_1"),
            "row_count_score": debug_dict.get("row_count_score"),
            "max_missing_score": debug_dict.get("max_missing_score"),
            "confidence": debug_dict.get("confidence"),
            "credibility_weight": debug_dict.get("credibility_weight"),
        }
        result_queue.put({"score": true_combined_score, "components": components})
    except Exception:
        result_queue.put({"score": 0.0, "components": None})


def _value_score_with_timeout(target_file_location: str, ground_truth_location: str,
                              gt_cache_path: str = "", weights: dict | None = None,
                              confidence: float | None = None, column_type_weights: dict | None = None,
                              credibility_weight: float | None = None):
    """Run value_based scoring in a child process with a hard timeout.

    FD-mining timeouts are handled internally by relative_csv_score() (full
    table, then a truncated retry) -- this outer timeout only needs to catch
    a genuinely stuck/broken worker, not do its own truncate-and-retry.

    confidence: optional self-reported LLM confidence (0.0-1.0), forwarded to
        value_based_relative_csv_score as the 5th score_1 component.
    column_type_weights: optional per-column-type sub-metric weights, forwarded
        to value_based_relative_csv_score.
    credibility_weight: optional pipeline-frequency-based credibility signal
        (0.0-1.0), forwarded to value_based_relative_csv_score as the 6th
        score_1 component.

    Returns (score, components) -- components is a dict of the raw
    (unweighted) score_1 inputs, or None on timeout/error.
    """
    q = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=_value_score_worker,
        args=(target_file_location, ground_truth_location, q, gt_cache_path, weights,
              confidence, column_type_weights, credibility_weight),
        # relative_csv_score() spawns its own child process for FD mining
        # (eval_score/score.py's _run_fdtool) -- a daemonic process can't have
        # children, so this parent must not be daemonic either.
        daemon=False,
    )
    p.start()
    p.join(timeout=_SCORE_TIMEOUT)
    if p.is_alive():
        p.terminate()
        p.join()
        return 0.0, None
    try:
        result = q.get_nowait()
        return result["score"], result["components"]
    except Exception:
        return 0.0, None


def _score_and_validate_output(
    target_file_location: str,
    ground_truth_location: str,
    validation_mode: str,
    reward_mode: str,
    gt_cache_path: str = "",
    score_weights: dict | None = None,
    confidence: float | None = None,
    column_type_weights: dict | None = None,
    credibility_weight: float | None = None,
):
    """
    Load output + ground truth and compute only the metric required by reward_mode:
      - "score"           : relative_csv_score (FD + column map + distribution)
      - "det_score_value" : value_based_relative_csv_score (Jaccard-aligned columns + value-based distribution)
      - "validation"      : avg_similarity from compare_lists/tables_matching (per-col × per-row)
      - "partial"         : fuzzy column-match ratio from compare_tables_fuzzy

    Returns (reward, is_correct, components) where is_correct is derived from
    reward >= threshold. components is a dict of the raw (unweighted)
    score_1 inputs when reward_mode="det_score_value" (None otherwise, and
    None on timeout/scoring error) -- logged regardless of score_weights so
    the score can be recomputed under different weights later.
    gt_cache_path: path to pre-computed GT JSON cache; passed to subprocess workers to
                   skip per-iteration FD mining and self-column-map on ground truth.
    score_weights: optional score_1 component weights (fd_f1/avg_col_score_1/
                   row_count_score/max_missing_score/confidence/credibility_weight),
                   only used when reward_mode="det_score_value". Defaults to
                   equal weights.
    confidence: optional self-reported LLM confidence (0.0-1.0) that the
                output matches the target -- only meaningful (non-None) on
                mcts_critique calls, which parse it from the $CONFIDENCE$
                block. Folded into score_1 as its 5th component when
                reward_mode="det_score_value"; ignored otherwise.
    column_type_weights: optional per-column-type (float/int/id/cat) sub-metric
                weights feeding avg_col_score_1, only used when
                reward_mode="det_score_value". Defaults to the original
                hardcoded per-type formulas.
    credibility_weight: optional pipeline-frequency-based credibility signal
                (0.0-1.0), computed from the case-wide pipeline occurrence
                count (see _record_pipeline_confidence/_credibility_weight_from_occurrences).
                Folded into score_1 as its 6th component when
                reward_mode="det_score_value"; ignored otherwise.
    """
    df_output = pd.read_csv(target_file_location, low_memory=False)
    df_gt = pd.read_csv(ground_truth_location, low_memory=False)
    df_gt = drop_leading_index_col_if_present(df_gt)

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
            target_file_location, ground_truth_location, gt_cache_path,
            weights=score_weights, confidence=confidence, column_type_weights=column_type_weights,
            credibility_weight=credibility_weight,
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
    COLUMN_TRANSFORM needs no special case: the trailing split() handles it, and
    it does not collide with the "AGGREGATE :" prefix test above.  (Neither did
    the pre-merge COLUMN_AGGREGATION, which also started "COLUMN_".)  Legacy
    COLUMN_AGGREGATION / FORMAT_DATETIME / PROJECT steps are rewritten upstream
    by _canonicalize_column_ops, so they do not reach here in normal operation.
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


# Pre-merge column-level operator names → the unified operator. See
# _LEGACY_OPERATOR_ALIASES in auto_suggest_llm_util.py for the same mapping applied
# at candidate-parse time; this one covers histories arriving from simulation,
# critique and replayed logs.
_LEGACY_COLUMN_OPS = ("COLUMN_AGGREGATION", "FORMAT_DATETIME", "PROJECT")


def _canonicalize_column_ops(history: List[str]) -> List[str]:
    """Rewrite pre-merge column-level steps to COLUMN_TRANSFORM.

    COLUMN_AGGREGATION, FORMAT_DATETIME and PROJECT were three special cases of the
    same row-preserving column map and are now one COLUMN_TRANSFORM operator. Their
    configuration payloads were already a bracketed "target = expr" list (PROJECT
    used "source -> target", which the execution prompt still accepts), so only the
    operator name ahead of the colon changes — the payload is passed through
    untouched.

    Applied wherever a history enters the tree from outside the expansion layer
    (simulation, critique, replayed logs), so a stale operator name does not create
    a tree child keyed under a vocabulary that no longer exists.

    Steps that do not start with a legacy name are returned unchanged.
    """
    result: List[str] = []
    for step in history:
        for legacy in _LEGACY_COLUMN_OPS:
            if step == legacy:
                result.append("COLUMN_TRANSFORM")
                break
            if step.startswith(f"{legacy} :"):
                # Swap only the operator name; the " : <payload>" tail is kept
                # exactly as-is (slicing at len(legacy), NOT len(legacy)+1, or the
                # separator is duplicated into "COLUMN_TRANSFORM :: ...").
                result.append("COLUMN_TRANSFORM" + step[len(legacy):])
                break
        else:
            result.append(step)
    return result


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


def _parse_pipeline_confidence(response_text: str, logger, tag: str = "_parse_pipeline_confidence") -> tuple[float | None, str]:
    """
    Parse the $CONFIDENCE$...$END_CONFIDENCE$ block from a simulate/critique LLM
    response. Expects a single decimal number in [0.0, 1.0]. Returns
    (confidence_float, raw_text). confidence_float is None if the block is
    missing or doesn't contain a parseable number; out-of-range values are
    clamped into [0.0, 1.0] (with a warning) rather than discarded, since the
    model's intent (very low/very high) is still clear.
    """
    match = re.search(r"\$CONFIDENCE\$(.*?)\$END_CONFIDENCE\$", response_text, re.DOTALL)
    if not match:
        logger.warning(f"[{tag}] No $CONFIDENCE$ block found in LLM response.")
        return None, ""
    raw_text = match.group(1).strip()
    num_match = re.search(r"-?\d+(?:\.\d+)?", raw_text)
    if not num_match:
        logger.warning(f"[{tag}] Unparseable confidence value: {raw_text!r}")
        return None, raw_text
    confidence = float(num_match.group(0))
    if not (0.0 <= confidence <= 1.0):
        logger.warning(f"[{tag}] Confidence {confidence} out of [0,1], clamping.")
        confidence = max(0.0, min(1.0, confidence))
    return confidence, raw_text


def _record_pipeline_confidence(
    state: "MCTSGraphState", full_history: List[str], self_reported_confidence: float | None
) -> tuple[float, int]:
    """
    Update the case-wide pipeline confidence/frequency table with one more
    occurrence of `full_history` (from either simulate or critique) and its
    self-reported $CONFIDENCE$ value for this occurrence, then return
    (blended_confidence, occurrences) -- occurrences is this pipeline's
    updated case-wide count, also used by callers to compute
    credibility_weight = occurrences / (occurrences + k) (see
    get_length_score_weights' per-length `k`).

        blended = avg_self_reported_confidence(pipeline) * (1 - 0.5 ** occurrences(pipeline))

    A single LLM confidence rating is unreliable on its own (limited context —
    it can rate a bad pipeline as confidently as a good one). But when the
    exact same full pipeline is independently regenerated across iterations
    (by simulate and/or critique) AND is rated confidently each time, that
    convergence is real signal. A pipeline seen once has its self-reported
    confidence heavily discounted (occurrences=1 -> 0.5x multiplier);
    repeated, consistently-confident pipelines approach their raw average
    confidence as occurrences grow.

    Mutates state["pipeline_confidence_stats"] in place (case-wide dict that
    persists across iterations, like state["root"]).
    """
    key = tuple(_canonicalize_column_ops(_split_groupby_aggregate(full_history)))
    stats = state["pipeline_confidence_stats"].setdefault(
        key, {"occurrences": 0, "conf_sum": 0.0, "conf_count": 0}
    )
    stats["occurrences"] += 1
    if self_reported_confidence is not None:
        stats["conf_sum"] += self_reported_confidence
        stats["conf_count"] += 1

    avg_conf = stats["conf_sum"] / stats["conf_count"] if stats["conf_count"] > 0 else 0.0
    blended = avg_conf * (1 - 0.5 ** stats["occurrences"])
    return round(blended, 4), stats["occurrences"]


def _credibility_weight_from_occurrences(occurrences: int, k: float | None) -> float | None:
    """credibility_weight = occurrences / (occurrences + k). None if k isn't
    configured for this case's length (see get_length_score_weights)."""
    if k is None:
        return None
    return round(occurrences / (occurrences + k), 4)


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
    path [root, ..., leaf] — leaf is the deepest node actually reached, which
    may be shorter than `steps` if a parent was already at MAX_CHILDREN and
    the step didn't match an existing child (see below).

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
        elif len(node.children) < MCTSNode.MAX_CHILDREN:
            op_type = _parse_op_type(step)
            node = node.add_child(step, child_history, operator_type=op_type)
        else:
            # node is already at the cap and this exact step isn't one of its
            # existing children — never exceed MAX_CHILDREN. Stop the walk
            # here; state["best_score"]/["best_script"] tracking (separate
            # from tree nodes) still captures the critique/simulate result,
            # just without a dedicated tree slot for this specific variant.
            break
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
        query_vector=state.get("local_rag_query_vector"),
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


# ──────────────────────────────────────────────────────────────────────────────
# Partial-pipeline execution — for ranking hints_v3 JOIN candidates against the
# real intermediate schema at a search node (not simulation/scoring; see
# prompts/partial_pipeline_execution.py for why this can't reuse
# _simulate_get_python — that path lets the LLM extend/complete the plan).
# ──────────────────────────────────────────────────────────────────────────────

_PARTIAL_PIPELINE_TABLE_CACHE: Dict[tuple, Tuple[Optional[pd.DataFrame], bool]] = {}


def _execute_partial_pipeline_only(
    rollout_history: List[str],
    csv_save_path: str,
    state: "MCTSGraphState",
) -> str:
    """Ask the LLM to generate code implementing EXACTLY rollout_history (no
    more, no less), execute it, retry up to _MAX_CODE_TRIALS times on error.
    Returns 'Success' or the last error string.
    """
    config = state["config"]
    error_str = ""
    response = ""
    for trial in range(_MAX_CODE_TRIALS):
        try:
            prompt = get_prompt(
                prompt_type="partial_pipeline_execute",
                max_tokens=config.token_limit,
                model=config.model,
                allowed_operation_list=OPERATOR_TYPES,
                operation_history=rollout_history,
                target_data_name=config.target_data_name,
                target_data_schema="",
                target_samples="",
                file_count=config.file_count,
                source_data_name_list=config.source_data_name_list,
                source_data_schema_list=config.source_data_schema_list,
                directory=config.directory,
                len_idx_target_idx=config.len_idx_target_idx,
                error_string=error_str,
                csv_save_path=csv_save_path,
                data_split=getattr(config, "data_split", "test"),
            )
        except Exception:
            config.logger.warning(
                f"[partial_exec] get_prompt failed (trial {trial}): "
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
            type="MCTS Partial Pipeline Exec",
        )

        pattern = re.compile(r"```[Pp]ython(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res[0])
        if not match:
            error_str += "No valid Python code block found in LLM response.\n"
            config.logger.warning(f"[partial_exec] No code block (trial {trial})")
            continue

        script = match.group(1).strip()
        response = execute_python(script)
        error_str += response + "\n"
        config.logger.info(f"[partial_exec] trial {trial}: {response}")

        if response == "Success":
            break

    return response


def _get_partial_pipeline_table(
    rollout_history: List[str],
    state: "MCTSGraphState",
) -> Tuple[Optional[pd.DataFrame], bool]:
    """Get the REAL dataframe of the pipeline as built so far, by asking the
    LLM to generate + execute code for EXACTLY rollout_history (nothing more).
    Returns (df, True) on success, (None, False) if code generation/execution
    failed — callers should skip ranking for this call rather than trust a
    stale/unknown state.

    Shared by JOIN's necessity (schema only, via _get_partial_pipeline_schema
    below) and GROUP BY's combined_dvr_delta (needs row data) — one execution,
    one cache, regardless of which operator type is being ranked at a node.
    """
    if not rollout_history:
        return pd.DataFrame(), True  # tree root: mapping = 0, nothing executed yet

    key = tuple(rollout_history)
    if key in _PARTIAL_PIPELINE_TABLE_CACHE:
        return _PARTIAL_PIPELINE_TABLE_CACHE[key]

    config = state["config"]
    scratch_csv = (
        f"{config.directory}/length{config.len_idx_target_idx}"
        f"/join_rank_scratch_{len(rollout_history)}_{abs(hash(key))}.csv"
    )
    response = _execute_partial_pipeline_only(rollout_history, scratch_csv, state)
    result: Tuple[Optional[pd.DataFrame], bool] = (None, False)
    if response == "Success" and os.path.exists(scratch_csv):
        try:
            df = pd.read_csv(scratch_csv, low_memory=False)
            result = (df, True)
        except Exception:
            config.logger.warning(
                f"[partial_exec] Failed to read scratch CSV {scratch_csv}: "
                f"{traceback.format_exc()}"
            )
    # The scratch file's only purpose is to get its contents into `result`
    # (cached in-memory below) — leaving it on disk serves nothing and, left
    # unchecked across many candidates/cases/iterations, silently fills the
    # benchmark data directories. Remove it once read (or on any leftover
    # partial/failed write), regardless of whether the read succeeded.
    if os.path.exists(scratch_csv):
        try:
            os.remove(scratch_csv)
        except OSError:
            config.logger.warning(
                f"[partial_exec] Failed to remove scratch CSV {scratch_csv}: "
                f"{traceback.format_exc()}"
            )
    _PARTIAL_PIPELINE_TABLE_CACHE[key] = result
    return result


def _get_partial_pipeline_schema(
    rollout_history: List[str],
    state: "MCTSGraphState",
) -> Tuple[Optional[set], bool]:
    """Thin wrapper over _get_partial_pipeline_table for callers (JOIN's
    necessity) that only need the column schema, not row data."""
    df, ok = _get_partial_pipeline_table(rollout_history, state)
    return (set(df.columns) if ok else None), ok


def _simulate_operator_level(state: "MCTSGraphState") -> tuple:
    """
    Operator-level simulation: mirrors the multistep process in multi_step.py.

    Starting from rollout_history (partial plan from expansion), iteratively
    asks the LLM for each next operator and configures it, building sim_history
    one step at a time until NO_MORE_OPERATION, then generates Python code.

    Returns (script: str, response: str, sim_history: List[str],
             confidence_raw: tuple[float | None, str]). This mode has no single
    $CONFIDENCE$-bearing LLM call (the plan is built step-by-step), so
    confidence_raw is always (None, "").
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
                query_vector=state.get("local_rag_query_vector"),
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

            elif operation in ("COLUMN_TRANSFORM",) + _LEGACY_COLUMN_OPS:
                # COLUMN_TRANSFORM has no dedicated configure prompt yet, so
                # operator-mode simulation records the bare step and lets code-gen
                # infer the columns. Keeping the step (rather than falling through to
                # the skip below) preserves the plan; a configure prompt in
                # prompts/configuration_prompts.py is the follow-up.
                # The legacy names are accepted so a model still emitting the
                # pre-merge vocabulary is normalised here rather than skipped.
                configured_step = "COLUMN_TRANSFORM"

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
                        df_gt = drop_leading_index_col_if_present(df_gt)
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
    return script, response, sim_history, (None, "")


def _simulate_pipeline_level(state: "MCTSGraphState") -> tuple:
    """
    Pipeline-level simulation (original behaviour): given the expanded node's
    operation history, ask the LLM to generate a COMPLETE Python script in one
    shot via the 'mcts_simulate' prompt, then execute it.

    Returns (script: str, response: str, full_history: List[str],
             confidence_raw: tuple[float | None, str]) where confidence_raw is
    (self_reported_confidence, raw_text) parsed from the $CONFIDENCE$ block --
    blending into the case-wide pipeline confidence table happens in simulate().
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]
    target_file_location: str = state["target_file_location"]

    rag_hints = get_rag_hints(
        state.get("local_rag_db_path", ""),
        rollout_history,
        query_vector=state.get("local_rag_query_vector"),
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

    # Parse $CONFIDENCE$...$END_CONFIDENCE$ block from the last LLM response.
    self_reported_confidence, confidence_raw = (None, "")
    if res:
        self_reported_confidence, confidence_raw = _parse_pipeline_confidence(
            res[0], config.logger, tag="simulate/pipeline"
        )

    return script, response, full_history, (self_reported_confidence, confidence_raw)


# ─────────────────────────────────────────────────────────────────────────────
# Node 1: mcts_select
# ─────────────────────────────────────────────────────────────────────────────


def mcts_select(state: MCTSGraphState) -> dict:
    """
    Tree Policy (UCB1 + prior-based FPU): walk from root until we reach a node that either
      (a) is not fully expanded (fewer than MAX_CHILDREN children, and not
          saturated), or
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
        node = node.best_child()
        path.append(node)

    config.logger.info(
        f"[MCTS Select] Iter {state['iteration']}: "
        f"selected depth={len(path) - 1}, op={node.operator_type}, "
        f"visits={node.visits}, children={len(node.children)}"
    )

    return {
        "selected_node": node,
        "last_selected_leaf": node,
        "selection_path": path,
        "rollout_history": list(node.operation_history),
        "rollout_step": len(node.operation_history),
        "in_rollout": False,
        "current_operator": "",
        "current_script": "",
        "current_score": 0.0,
        "current_response": "",
        "current_confidence": None,
        "critique_attempted": False,  # reset each iteration
        "log_messages": state["log_messages"]
        + [
            f"Iter {state['iteration']}: selected node depth={len(path)-1} op={node.operator_type}"
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 2: next_operator_step  (EXPANSION — single mcts_expand LLM call)
# ─────────────────────────────────────────────────────────────────────────────


_OPERATOR_CONFIG_LAMBDA = 0.5  # tunable: S(o,c) = λ·S_LLM + (1-λ)·S_rule
# Number of candidates requested from the LLM per expand call — independent
# of MCTSNode.MAX_CHILDREN (the tree's per-node child cap). The LLM's
# response is a ranked list; the distinct operator types in first-appearance
# order become this call's type-priority order (see _type_priority_order).
_EXPAND_LLM_K = 3
# Split of the LLM's signal between "which operator TYPE" and "which CONFIG
# of that type" (must sum to 1.0):
#   S_LLM = _W_TYPE * S_type + _W_CONFIG * S_config
# _W_TYPE is the share a candidate earns purely for belonging to a type the
# LLM endorsed — so a rule-engine-proposed config of the LLM's top type
# scores _W_TYPE (0.8) rather than 0, while an exact config match still
# reaches 1.0. Because S_type is itself rank-normalised over the types the
# LLM named, this credit degrades automatically for lower-ranked types
# (0.8 for rank 1 of 5, 0.64 for rank 2, ...) instead of being one flat
# hand-tuned constant.
_W_TYPE = 0.8
_W_CONFIG = 0.2
# Cap on how many RULE-ONLY candidates (s_llm == 0.0, i.e. never proposed by
# the LLM) from one operator type's pool are eligible to be admitted. LLM-
# sourced candidates (s_llm > 0, "both" or "llm-only") are never capped here.
# Without this, a type whose rule engine returns a large ranked list (e.g.
# GROUP_BY's per-column statistical scoring can return 80+ candidates) could
# use up all of a node's remaining room by itself once it's this call's
# highest-priority type.
_RULE_INJECT_TOP_K = 3


def _type_priority_order(candidates: List[Tuple[str, str]]) -> List[str]:
    """Distinct operator types from the LLM's ranked candidate list, in
    first-appearance order (dedup, order-preserving). E.g.
    [(GROUP_BY,a),(GROUP_BY,b),(JOIN,c)] -> ["GROUP_BY", "JOIN"]. This is the
    type-priority order next_operator_step fills a node's remaining child
    slots in — types not mentioned here get no turn this call.
    """
    order: List[str] = []
    seen: set = set()
    for op_type, _cfg in candidates:
        if op_type not in seen:
            seen.add(op_type)
            order.append(op_type)
    return order


def _cap_rule_only_candidates(
    ranked: List[Tuple[str, float, float, float, float]],
    top_k: int = _RULE_INJECT_TOP_K,
) -> List[Tuple[str, float, float, float, float]]:
    """Filter one operator type's scored pool (as returned by
    _score_operator_type_pool, sorted best-first by `combined`): keep every
    LLM-proposed candidate uncapped, keep only the first `top_k` rule-only
    candidates. Preserves input order (already score-sorted), so "first
    top_k rule-only" is "top_k by score."

    Rule-only is detected via S_config == 0.0, NOT S_llm: since S_llm now
    carries the type-level term (_W_TYPE * S_type), a rule-only candidate of
    an LLM-endorsed type has S_llm > 0. S_config is the part that is non-zero
    only when the LLM proposed that exact config.
    """
    kept: List[Tuple[str, float, float, float, float]] = []
    rule_only_kept = 0
    for cfg, s_llm, s_rule, combined, s_config in ranked:
        if s_config == 0.0:
            if rule_only_kept >= top_k:
                continue
            rule_only_kept += 1
        kept.append((cfg, s_llm, s_rule, combined, s_config))
    return kept


def _rank_join_v3_candidates(
    config, rollout_history: List[str], state: "MCTSGraphState"
) -> List[Tuple[str, float]]:
    """Combine the precomputed static (evidence, name_score) JOIN candidates
    with a freshly-computed necessity term against the REAL current schema
    (via _get_partial_pipeline_schema). All candidates share the same
    rollout_history, so the partial-pipeline execution only runs once here,
    not once per candidate. Returns [(configured_step, score), ...] sorted
    best-first, or [] if hints_v3 JOIN candidates weren't computed for this
    case, or if the current schema couldn't be reliably determined.
    """
    static_candidates = getattr(config, "hint_join_v3_candidates", None)
    source_columns = getattr(config, "hint_join_v3_source_columns", None)
    target_columns = getattr(config, "hint_join_v3_target_columns", None)
    if not static_candidates or not source_columns or target_columns is None:
        return []

    current_schema, is_reliable = _get_partial_pipeline_schema(rollout_history, state)
    if not is_reliable:
        return []

    scored = []
    for cand in static_candidates:
        t1, c1, t2, c2 = cand["t1"], cand["c1"], cand["t2"], cand["c2"]
        t1_cols = set(source_columns.get(t1, []))
        t2_cols = set(source_columns.get(t2, []))
        # What this candidate would add to the schema: the union of both
        # tables' columns, minus whatever's already present. Deliberately
        # NOT "classify which side is new" — a table's join-key column will
        # almost always already overlap current_schema (that's what makes it
        # joinable), which would wrongly mark an unjoined table as "not new"
        # if its other columns were checked via any-overlap instead of a
        # plain set difference.
        new_cols = (t1_cols | t2_cols) - current_schema

        nec = hint_v3.necessity(new_cols, current_schema, target_columns)
        final = (cand["evidence"] + cand["name_score"] + nec) / 3.0
        cfg = f"JOIN : [[{t1}, {t2}]] columns=[[{t1}.{c1}, {t2}.{c2}]]"
        scored.append((cfg, final))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


_GROUPBY_COMBO_TOP_N = 5    # how many top individual columns feed heuristic combinations
_GROUPBY_COMBO_MAX_SIZE = 2  # max columns per heuristic combination


def _resolve_intermediate_table_for_groupby(
    rollout_history: List[str], state: "MCTSGraphState", config
) -> Tuple[Optional[pd.DataFrame], bool]:
    """Depth-0 fallback + real-execution resolution for GROUP BY's
    combined_dvr_delta (GROUP_BY_RANKING_DESIGN_README.md): use the real
    executed intermediate table once a JOIN/UNION has happened in
    rollout_history; before that (nothing to execute yet), fall back to the
    sole source table, or whichever source table overlaps the target schema
    most (hint_v3.best_overlapping_table, same technique get_union_hints uses).
    """
    has_join_or_union = any(
        _parse_op_type(step) in ("JOIN", "UNION") for step in rollout_history
    )
    if has_join_or_union:
        return _get_partial_pipeline_table(rollout_history, state)

    try:
        tables = hint_v3.load_tables(
            config.directory, config.source_data_name_list, config.len_idx_target_idx
        )
    except Exception:
        return None, False
    if not tables:
        return None, False
    if len(tables) == 1:
        return next(iter(tables.values())), True

    groupby_static = getattr(config, "hint_groupby_v3_candidates", None) or {}
    target_columns = groupby_static.get("target_columns", [])
    best_table = hint_v3.best_overlapping_table(tables, target_columns)
    if best_table is None:
        return None, False
    return tables[best_table], True


def _rank_groupby_v3_candidates(
    config, rollout_history: List[str], state: "MCTSGraphState"
) -> List[Tuple[str, float]]:
    """Unified GROUP BY ranking: one formula (leftness_prior_combined +
    combined_dvr_delta + groupby_fd_score, averaged) for every candidate,
    regardless of whether it came from the hint_v3 statistical pool or the
    FD algorithm — no path split (see GROUP_BY_RANKING_DESIGN_README.md).
    Returns [(configured_step, score), ...] sorted best-first, or [] if
    hints_v3 GROUP BY candidates weren't computed for this case, or if the
    intermediate table couldn't be resolved.
    """
    static = getattr(config, "hint_groupby_v3_candidates", None)
    if not static:
        return []
    individual_columns = static.get("individual_columns", [])
    fd_keys = static.get("fd_keys", set())
    source_columns = static.get("source_columns", {})
    target_columns = static.get("target_columns", [])
    if not individual_columns or not target_columns:
        return []

    intermediate_df, is_reliable = _resolve_intermediate_table_for_groupby(
        rollout_history, state, config
    )
    if not is_reliable or intermediate_df is None:
        return []

    try:
        target_file = os.path.join(
            config.directory, f"length{config.len_idx_target_idx}", "target.csv"
        )
        target_df = pd.read_csv(target_file, low_memory=False)
        # Name-based, not positional: smart_building targets start with REAL data
        # (datetime/cst), so an unconditional drop removes a target column and
        # corrupts the S_rule ranking these candidates are ordered by.
        target_df = drop_leading_index_col_if_present(target_df)
    except Exception:
        return []

    def _score(entries):
        # entries: list of (t, c, leftness, matched_target_col)
        leftness_prior = sum(1 - li for _, _, li, _ in entries) / len(entries)
        source_cols = [c for _, c, _, _ in entries]
        matched = [mt for _, _, _, mt in entries]
        if any(mt is None for mt in matched) or not set(source_cols).issubset(
            set(intermediate_df.columns)
        ):
            dvr_delta = 0.0
        else:
            try:
                dvr_delta = hint_v3.combined_dvr_delta(
                    intermediate_df, target_df, source_cols, matched
                )
            except Exception:
                dvr_delta = 0.0
        fd = hint_v3.groupby_fd_score(source_cols, fd_keys)
        return (leftness_prior + dvr_delta + fd) / 3.0

    scored: List[Tuple[str, float]] = []

    # Individual columns — the hint_v3 statistical pool
    for entry in individual_columns:
        s = _score([(entry["t"], entry["c"], entry["leftness"], entry["matched_target_col"])])
        cfg = f"GROUP_BY : [{entry['t']}.{entry['c']}]"
        scored.append((cfg, s))

    # Bounded heuristic combinations of the top individual columns
    top_n = sorted(individual_columns, key=lambda e: e["leftness"])[:_GROUPBY_COMBO_TOP_N]
    for combo_size in range(2, _GROUPBY_COMBO_MAX_SIZE + 1):
        for combo in combinations(top_n, combo_size):
            entries = [(e["t"], e["c"], e["leftness"], e["matched_target_col"]) for e in combo]
            s = _score(entries)
            cols_str = ", ".join(f"{e['t']}.{e['c']}" for e in combo)
            scored.append((f"GROUP_BY : [{cols_str}]", s))

    # FD-discovered determinant sets — added directly as their own candidates,
    # resolved to source tables so they can be formatted as a configured_step
    col_lookup = {(e["t"], e["c"]): e for e in individual_columns}
    for fd_key in fd_keys:
        resolved = []
        ok = True
        for col_name in fd_key:
            found = None
            for tname, cols in source_columns.items():
                if col_name in cols:
                    found = (tname, col_name)
                    break
            if found is None:
                ok = False
                break
            resolved.append(found)
        if not ok:
            continue
        entries = []
        for t, c in resolved:
            e = col_lookup.get((t, c))
            leftness = e["leftness"] if e else 0.5
            matched = e["matched_target_col"] if e else (c if c in target_columns else None)
            entries.append((t, c, leftness, matched))
        s = _score(entries)
        cols_str = ", ".join(f"{t}.{c}" for t, c in resolved)
        scored.append((f"GROUP_BY : [{cols_str}]", s))

    # The FD-discovered path and the heuristic-combination path can
    # independently produce the exact same column set (e.g. an FD pair that
    # also happens to fall within the top-N leftness combo pool) — dedupe by
    # configured_step, keeping the first (score is identical either way since
    # it's the same entries scored the same way).
    seen_cfgs = set()
    deduped: List[Tuple[str, float]] = []
    for cfg, s in scored:
        if cfg in seen_cfgs:
            continue
        seen_cfgs.add(cfg)
        deduped.append((cfg, s))

    deduped.sort(key=lambda x: x[1], reverse=True)
    return deduped


def _parse_groupby_columns(groupby_cfg: str) -> set:
    # "GROUP_BY : [t1.c1, t1.c2]" -> {"c1", "c2"} (bare column names — a
    # group-by key shouldn't also be an aggregation target, regardless of
    # which table it came from).
    m = re.search(r"\[(.*)\]", groupby_cfg, re.DOTALL)
    if not m:
        return set()
    cols = set()
    for part in m.group(1).split(","):
        part = part.strip()
        if not part:
            continue
        cols.add(part.split(".")[-1])
    return cols


def _parse_aggregate_pairs(aggregate_cfg: str) -> List[Tuple[str, str, str]]:
    # "AGGREGATE : [SUM(t1.c1), COUNT DISTINCT(t2.c2)]" ->
    # [("SUM", "t1", "c1"), ("COUNT", "t2", "c2")] — normalizes multi-word
    # function names (e.g. "COUNT DISTINCT") down to their base function.
    pairs = []
    for func_raw, col_ref in re.findall(r"([A-Za-z_]+(?:\s+[A-Za-z_]+)?)\(([^)]+)\)", aggregate_cfg):
        func = func_raw.strip().split()[0].upper()
        col_ref = col_ref.strip()
        if "." in col_ref:
            table, col = col_ref.rsplit(".", 1)
        else:
            table, col = "", col_ref
        pairs.append((func, table, col))
    return pairs


def _rank_aggregate_by_llm_only(
    candidates: List[Tuple[str, str]],
) -> List[Tuple[str, str, float, float, float]]:
    """Fallback ranking when the real S_rule can't be computed (no rollout
    history, or the intermediate/target table couldn't be resolved): S_rule=0
    for everything, degrading to pure LLM rank order — same convention
    _score_operator_type_pool uses for operator types with no rule engine.
    """
    k = len(candidates)
    scored = []
    for rank, (op, cfg) in enumerate(candidates, start=1):
        s_llm = (k - rank + 1) / k if k > 0 else 0.0
        combined = _OPERATOR_CONFIG_LAMBDA * s_llm
        scored.append((op, cfg, s_llm, 0.0, combined))
    return scored


def _compute_aggregation_evidence(
    rollout_history: List[str],
    state: "MCTSGraphState",
    config,
) -> str:
    """Render hint_v3's distribution-based aggregation evidence for the GROUP
    BY key already committed in rollout_history[-1], for injection into the
    AGGREGATE expand prompt. Returns "" if the intermediate or target table
    can't be resolved, so the prompt simply omits the block.
    """
    if not rollout_history:
        return ""
    try:
        group_by_cols = _parse_groupby_columns(rollout_history[-1])
        if not group_by_cols:
            return ""

        intermediate_df, is_reliable = _resolve_intermediate_table_for_groupby(
            rollout_history[:-1], state, config
        )
        if not is_reliable or intermediate_df is None:
            return ""

        target_file = os.path.join(
            config.directory, f"length{config.len_idx_target_idx}", "target.csv"
        )
        target_df = pd.read_csv(target_file, low_memory=False)
        # Name-based, not positional: smart_building targets start with REAL data
        # (datetime/cst), so an unconditional drop removes a target column and
        # corrupts the S_rule ranking these candidates are ordered by.
        target_df = drop_leading_index_col_if_present(target_df)

        return hint_v3.get_aggregation_distribution_hints(
            intermediate_df, target_df, group_by_cols
        )
    except Exception:
        config.logger.warning(
            f"[expand] aggregation evidence failed: {traceback.format_exc()}"
        )
        return ""


def _rerank_aggregate_llm_candidates(
    candidates: List[Tuple[str, str]],
    rollout_history: List[str],
    state: "MCTSGraphState",
    config,
) -> List[Tuple[str, str, float, float, float]]:
    """Score the LLM's own AGGREGATE proposals using
    S(o,c) = λ·S_LLM + (1-λ)·S_rule, where S_rule is
    aggregation_condition_bucket/score (dtype + magnitude-ratio conditions
    against the real pre-GROUP_BY intermediate table and target) and S_LLM is
    derived from the LLM's own rank position among these candidates. No new
    candidates injected, no new LLM call.

    Returns [(op, cfg, s_llm, s_rule, combined), ...] sorted best-first —
    same shape as _score_operator_type_pool, so AGGREGATE candidates feed the
    same unified pooling/prior logic as every other operator type. Falls back
    to LLM-rank-only scoring (_rank_aggregate_by_llm_only) if the intermediate
    or target table can't be resolved.
    """
    if not rollout_history or not candidates:
        return _rank_aggregate_by_llm_only(candidates)

    group_by_cols = _parse_groupby_columns(rollout_history[-1])

    intermediate_df, is_reliable = _resolve_intermediate_table_for_groupby(
        rollout_history[:-1], state, config
    )
    if not is_reliable or intermediate_df is None:
        return _rank_aggregate_by_llm_only(candidates)

    try:
        target_file = os.path.join(
            config.directory, f"length{config.len_idx_target_idx}", "target.csv"
        )
        target_df = pd.read_csv(target_file, low_memory=False)
        # Name-based, not positional: smart_building targets start with REAL data
        # (datetime/cst), so an unconditional drop removes a target column and
        # corrupts the S_rule ranking these candidates are ordered by.
        target_df = drop_leading_index_col_if_present(target_df)
    except Exception:
        return _rank_aggregate_by_llm_only(candidates)

    bucket_cache: Dict[str, set] = {}

    def _pair_score(func: str, col: str) -> float:
        if col in group_by_cols:
            return 0.0
        if col not in bucket_cache:
            # Name-based match, not hint_v3.match()'s value-overlap check —
            # aggregation deliberately changes values (that's the point of
            # SUM/COUNT/etc.), so a genuine (source, target) aggregation pair
            # will usually share NO overlapping values; only the column name
            # is expected to persist across the transformation.
            if col not in intermediate_df.columns or col not in target_df.columns:
                bucket_cache[col] = set()
            else:
                bucket_cache[col] = hint_v3.aggregation_condition_bucket(
                    intermediate_df[col], target_df[col]
                )
        return hint_v3.aggregation_condition_score(bucket_cache[col], func)

    def _s_rule(op_type: str, cfg: str) -> float:
        if op_type != "AGGREGATE":
            return 0.0
        pairs = _parse_aggregate_pairs(cfg)
        if not pairs:
            return 0.0
        return sum(_pair_score(func, col) for func, _table, col in pairs) / len(pairs)

    k = len(candidates)
    scored = []
    for rank, (op, cfg) in enumerate(candidates, start=1):
        s_rule = _s_rule(op, cfg)
        s_llm = (k - rank + 1) / k if k > 0 else 0.0
        combined = (
            _OPERATOR_CONFIG_LAMBDA * s_llm + (1 - _OPERATOR_CONFIG_LAMBDA) * s_rule
        )
        scored.append((op, cfg, s_llm, s_rule, combined))
    scored.sort(key=lambda x: x[4], reverse=True)
    return scored


def _group_llm_candidates_by_type(candidates: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    # Preserves the LLM's rank order within each operator type.
    by_type: Dict[str, List[str]] = {}
    for op_type, cfg in candidates:
        by_type.setdefault(op_type, []).append(cfg)
    return by_type


def _score_operator_type_pool(
    op_type: str,
    llm_cfgs: List[str],
    config,
    rollout_history: List[str],
    state: "MCTSGraphState",
    s_type: float = 0.0,
) -> List[Tuple[str, float, float, float, float]]:
    """Build the unified LLM+rule pool for one operator type and score every
    candidate via S(o,c) = λ·S_LLM + (1-λ)·S_rule. S_rule comes from the FULL
    rule ranking for types with a rule engine (JOIN, GROUP_BY), not just its
    top-K, so an LLM-proposed candidate already in the rule's internal
    ranking gets its real score rather than a 0 fallback. Types with no rule
    engine get S_rule=0 for everything, degrading to pure LLM rank order.

    S_LLM is decomposed into the LLM's two independent signals — WHICH TYPE
    and WHICH CONFIG — instead of being all-or-nothing:

        S_LLM(c) = _W_TYPE * s_type  +  _W_CONFIG * S_config(c)

    where s_type (passed in by the caller) is the type's own priority rank
    score (M - r + 1)/M over the M distinct types the LLM named, and
    S_config(c) is the same rank normalisation applied WITHIN this type —
    (k - rank + 1)/k for a config the LLM actually proposed, 0 otherwise.

    This is what lets a rule-engine-proposed config of a type the LLM
    endorsed earn partial LLM credit (_W_TYPE * s_type) rather than a flat 0,
    while an exact config match still reaches the full 1.0, and a type the
    LLM never named still scores 0. The credit degrades naturally with the
    type's rank, so it needs no separately tuned constant.

    Logs the LLM's raw list, the rule engine's own standalone ranking (before
    any merging), and the final merged+scored pool with each candidate's
    source (llm-only / rule-only / both) — so the transformation from "what
    the LLM suggested" + "what the rule engine suggested" to "what the tree
    ended up with" is visible in the logs, not just the end result.

    Returns [(cfg, S_llm, S_rule, S_combined, S_config), ...] sorted
    best-first by S_combined. S_config is carried through so callers can tell
    a rule-only candidate (S_config == 0) from an LLM-proposed one even
    though S_llm is now non-zero for both.
    """
    if op_type == "JOIN":
        rule_ranked = _rank_join_v3_candidates(config, rollout_history, state)
    elif op_type == "GROUP_BY":
        rule_ranked = _rank_groupby_v3_candidates(config, rollout_history, state)
    else:
        rule_ranked = []

    config.logger.info(f"[expand/{op_type}] LLM proposed (rank order): {llm_cfgs}")
    config.logger.info(
        f"[expand/{op_type}] rule engine proposed (top 5 of {len(rule_ranked)}, "
        f"standalone, before merge): "
        f"{[(cfg, round(s, 3)) for cfg, s in rule_ranked[:5]]}"
    )

    rule_score = dict(rule_ranked)
    k = len(llm_cfgs)
    llm_rank = {cfg: rank for rank, cfg in enumerate(llm_cfgs, start=1)}

    pool_cfgs = set(llm_cfgs) | set(rule_score)
    scored = []
    for cfg in pool_cfgs:
        s_rule = rule_score.get(cfg, 0.0)
        s_config = (k - llm_rank[cfg] + 1) / k if cfg in llm_rank and k > 0 else 0.0
        s_llm = _W_TYPE * s_type + _W_CONFIG * s_config
        combined = (
            _OPERATOR_CONFIG_LAMBDA * s_llm + (1 - _OPERATOR_CONFIG_LAMBDA) * s_rule
        )
        source = (
            "both" if cfg in llm_rank and cfg in rule_score
            else "llm-only" if cfg in llm_rank
            else "rule-only"
        )
        scored.append((cfg, s_llm, s_rule, combined, s_config, source))

    scored.sort(key=lambda x: x[3], reverse=True)

    config.logger.info(
        f"[expand/{op_type}] merged+scored pool ({len(scored)} candidates, "
        f"S_type={s_type:.2f}): "
        + "; ".join(
            f"{cfg[:60]} [{source}] S_cfg={s_config:.2f} S_llm={s_llm:.2f} "
            f"S_rule={s_rule:.2f} S={combined:.3f}"
            for cfg, s_llm, s_rule, combined, s_config, source in scored[:10]
        )
        + (f" ... (+{len(scored) - 10} more)" if len(scored) > 10 else "")
    )

    return [
        (cfg, s_llm, s_rule, combined, s_config)
        for cfg, s_llm, s_rule, combined, s_config, _ in scored
    ]


def next_operator_step(state: MCTSGraphState) -> dict:
    """
    EXPANSION (Option B — batch expand, single simulate):
    One mcts_expand LLM call returns up to _EXPAND_LLM_K ranked candidates
    (independent of MAX_CHILDREN). The distinct operator TYPES in the order
    they first appear in that ranking define this call's type-priority order
    (see _type_priority_order). Types are filled one at a time in that order —
    each type's own LLM-proposed candidates plus (if it has a rule engine)
    the rule engine's top _RULE_INJECT_TOP_K rule-only candidates, scored with
    S(o,c) = λ·S_LLM + (1-λ)·S_rule and sorted within the type — until the
    node's remaining room (MAX_CHILDREN total) is used up. A lower-priority
    type is never touched once room runs out, even if one of its candidates
    would have scored higher in raw S(o,c) than an admitted higher-priority
    candidate.

    Logic
    -----
    1. Ask the LLM for _EXPAND_LLM_K candidates. NO_MORE_OPERATION is excluded
       from the allowed operators here so expansion always grows the tree —
       only simulation and critique may terminate a plan.
    2. Derive type-priority order from the LLM's own ranking, then walk types
       in that order, admitting each type's scored+capped candidates (in
       score order) until MAX_CHILDREN is reached. No per-type quota beyond
       the rule-only cap — a single type can use up all remaining room.
    3. If nothing was admitted, mark node saturated.
    4. Simulate the single best-scored candidate among everything actually
       admitted this call (never a candidate that didn't make the cut).
    5. Ultimate fallback (empty/unparseable response, or nothing admitted):
       saturate silently, re-simulate from existing prefix.
    """
    config = state["config"]
    rollout_history: List[str] = state["rollout_history"]
    selected_node: MCTSNode = state["selected_node"]
    selection_path: List[MCTSNode] = state["selection_path"]

    # Fixed candidate-request size, independent of MAX_CHILDREN (the tree cap).
    k = _EXPAND_LLM_K

    # Determine whether this is a forced AGGREGATE expansion (parent is GROUP_BY)
    # or a standard structural expansion.
    # • GROUP_BY parent   → only AGGREGATE is valid next; use aggregation expand prompt.
    # • AGGREGATE parent  → every structural type EXCEPT GROUP_BY (grouping an
    #                        already-aggregated table is never valid; this is what
    #                        produced GROUP_BY→AGGREGATE→GROUP_BY chains).
    # • All other nodes   → every structural op type is always offered, regardless
    #                        of whether one already has a child — multiple children
    #                        of the same type competing purely on score is the point.
    is_groupby_expansion = (selected_node.operator_type == "GROUP_BY")
    is_post_aggregate = (selected_node.operator_type == "AGGREGATE")
    explored_steps = list(selected_node.children.keys())  # configs already in tree

    if is_groupby_expansion:
        expand_prompt_type = "mcts_expand_aggregate"
        expand_ops = ["AGGREGATE"]
    else:
        expand_prompt_type = "mcts_expand"
        expand_ops = list(
            POST_AGGREGATE_EXPAND_OPS if is_post_aggregate else STRUCTURAL_EXPAND_OPS
        )
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
            query_vector=state.get("local_rag_query_vector"),
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
            agg_evidence=(
                _compute_aggregation_evidence(rollout_history, state, config)
                if is_groupby_expansion else ""
            ),
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

    # ── Build the type-priority-ordered candidate list: S(o,c) = λ·S_LLM + (1-λ)·S_rule ──
    # GROUP_BY parent → AGGREGATE is the only type (rerank, no new LLM call).
    # Any other parent → type_priority is the distinct operator types in the
    # order the LLM's own ranked response first mentions them; types it never
    # mentions get no turn this call. Within each type, candidates (LLM's own
    # plus, for JOIN/GROUP_BY, the rule engine's top _RULE_INJECT_TOP_K
    # rule-only candidates) are scored and kept in score order. Concatenating
    # per type in priority order (NOT a global cross-type sort) makes type
    # priority win first, S(o,c) only break ties/order within a type.
    # Each entry also carries the banded `prior` stored on the child node:
    #     prior = (N - r)/N + S_combined/N          (N = len(STRUCTURAL_EXPAND_OPS))
    # Rank r occupies the band [(N-r)/N, (N-r+1)/N], exactly 1/N wide, and
    # S_combined ∈ [0,1] always lands inside that one band — so ANY candidate
    # of a higher-priority type outranks EVERY candidate of a lower-priority
    # type, while S_combined orders candidates within a type. The AGGREGATE
    # branch has a single type, so it needs no banding and uses S_combined
    # directly (its children are only ever compared against each other).
    # Entries: (prior, combined, cfg, op_type, s_llm, s_rule).
    ordered_candidates: List[Tuple[float, float, str, str, float, float]] = []
    _n_band = len(STRUCTURAL_EXPAND_OPS)

    if is_groupby_expansion:
        if candidates:
            for op_type, cfg, s_llm, s_rule, combined in _rerank_aggregate_llm_candidates(
                candidates, rollout_history, state, config
            ):
                ordered_candidates.append((combined, combined, cfg, op_type, s_llm, s_rule))
    else:
        llm_by_type = _group_llm_candidates_by_type(candidates)
        type_priority = _type_priority_order(candidates)
        _m_types = len(type_priority)
        for rank, op_type in enumerate(type_priority, start=1):
            s_type = (_m_types - rank + 1) / _m_types if _m_types else 0.0
            ranked = _score_operator_type_pool(
                op_type, llm_by_type.get(op_type, []), config, rollout_history, state,
                s_type=s_type,
            )
            for cfg, s_llm, s_rule, combined, _s_cfg in _cap_rule_only_candidates(ranked):
                prior = (_n_band - rank) / _n_band + combined / _n_band
                ordered_candidates.append((prior, combined, cfg, op_type, s_llm, s_rule))

    # ── Admit candidates in type-priority order until MAX_CHILDREN is hit ───
    # No eviction of existing children — once full, anything later in
    # ordered_candidates (whether a lower-priority type or a lower-scored
    # config of the current type) is simply never admitted this call. A
    # candidate that already matches an existing child costs no room but is
    # still recorded as admitted (eligible for the simulation-target pick).
    existing_configs: set = set(selected_node.children.keys())
    new_configs_added: List[str] = []
    admitted: List[Tuple[float, float, str, str, float, float]] = []
    room = MCTSNode.MAX_CHILDREN - len(selected_node.children)

    for prior, combined, cfg, op_type, s_llm, s_rule in ordered_candidates:
        if cfg in existing_configs:
            admitted.append((prior, combined, cfg, op_type, s_llm, s_rule))
            continue
        if room <= 0:
            break
        child_history = rollout_history + [cfg]
        selected_node.add_child(cfg, child_history, operator_type=op_type, prior=prior)
        new_configs_added.append(cfg)
        existing_configs.add(cfg)
        admitted.append((prior, combined, cfg, op_type, s_llm, s_rule))
        room -= 1
        config.logger.info(
            f"[expand] Iter {state['iteration']}: added {op_type} "
            f"cfg={cfg[:100]} S_llm={s_llm:.2f} S_rule={s_rule:.2f} "
            f"S={combined:.3f} prior={prior:.3f} "
            f"(tree now has {len(selected_node.children)} children)"
        )

    # Saturation: LLM returned no new configs — mark so selection descends past this node
    if not new_configs_added and candidates:
        selected_node.saturated = True
        config.logger.info(
            f"[expand] Iter {state['iteration']}: all candidates already in tree — "
            f"node marked saturated"
        )

    # ── Simulation target: the single best-scored candidate ACTUALLY ADMITTED ──
    # (never a candidate that lost out on room — by construction that can no
    # longer happen, since admitted only ever grows via the loop above.)
    if admitted:
        # Ranked by the banded prior, so the LLM's type priority is respected
        # here too — a lower-priority type's candidate can never be simulated
        # over a higher-priority type's, whatever their raw S_combined.
        _best_prior, _best_combined, chosen_cfg, chosen_op, _best_s_llm, _best_s_rule = max(
            admitted, key=lambda a: a[0]
        )
        new_node = selected_node.children[chosen_cfg]
        new_history = rollout_history + [chosen_cfg]
        config.logger.info(
            f"[expand] Iter {state['iteration']}: simulating best-scored op={chosen_op} "
            f"| cfg={chosen_cfg[:80]} S={_best_combined:.3f} prior={_best_prior:.3f} "
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

    Updates: current_script, current_response, current_full_history, current_confidence.
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
            script, response, full_history, (self_reported_confidence, confidence_raw) = _simulate_operator_level(state)
        else:
            script, response, full_history, (self_reported_confidence, confidence_raw) = _simulate_pipeline_level(state)
    except CostBudgetExceeded as e:
        config.logger.warning(f"[simulate] {e} — stopping search.")
        return {
            "cost_budget_exhausted": True,
            "current_script": "",
            "current_response": "cost_budget_exhausted",
            "current_full_history": [],
            "current_confidence": 0.0,
            "current_credibility_weight": 0.0,
            "log_messages": state["log_messages"]
            + [f"[SIMULATE] iter={state['iteration']} COST_BUDGET_EXHAUSTED — no request sent"],
        }

    _result = "Success" if response == "Success" else "FAILED"

    # Blend this occurrence into the case-wide pipeline confidence/frequency table
    # (shared with critique) -- None if no plan was parsed.
    if full_history:
        confidence, occurrences = _record_pipeline_confidence(state, full_history, self_reported_confidence)
        credibility_weight = _credibility_weight_from_occurrences(occurrences, state.get("credibility_k"))
    else:
        confidence, occurrences, credibility_weight = None, 0, None

    return {
        "current_script": script,
        "current_response": response,
        "current_full_history": full_history,
        # Raw blended value (may be None if no plan was parsed) -- execute_and_score
        # forwards this as-is to scoring so a missing confidence is excluded/
        # renormalized rather than treated as a real zero. See _weighted_avg_available.
        "current_confidence": confidence,
        "current_credibility_weight": credibility_weight,
        "log_messages": state["log_messages"]
        + [
            f"[SIMULATE] iter={state['iteration']} mode={sim_mode} result={_result} "
            f"plan_steps={len(full_history)} "
            f"confidence: self_reported={confidence_raw!r} ({self_reported_confidence}) -> blended={confidence}, "
            f"credibility_weight: occurrences={occurrences} -> {credibility_weight}"
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
                confidence=state.get("current_confidence"),
                column_type_weights=state.get("column_type_weights"),
                credibility_weight=state.get("current_credibility_weight"),
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
                df_gt = drop_leading_index_col_if_present(df_gt)
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
    full_history = _canonicalize_column_ops(_split_groupby_aggregate(full_history))

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

    # Virtual visits for selection-only nodes when simulation diverged
    for node in reversed(selection_only_nodes):
        node.update(0.0)  # visits += 1, total_reward += 0

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
        crit_script, crit_score, _, _, _, _, _, _, _, _ = _run_critique_llm(state, best_script)
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
        df_gt = drop_leading_index_col_if_present(df_gt)
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
    Returns (new_script, new_score, new_response, validation_passed, critique_plan,
             score_components, confidence, confidence_raw, credibility_weight, llm_response).
    Loads ground truth internally for scoring. score_components is the raw
    (unweighted) score_1 inputs (det_score_value mode only), or None -- includes
    "confidence"/"credibility_weight" once available.
    critique_plan is a List[str] parsed from $PLAN$...$END_PLAN$ block, or [] if not found.
    confidence is the BLENDED pipeline confidence (self-reported x frequency, see
    _record_pipeline_confidence) used for scoring, or None if critique_plan was
    unparseable. confidence_raw is the raw $CONFIDENCE$ text from THIS call
    (pre-blend), or "" if the block is missing. credibility_weight is
    occurrences/(occurrences+k) for this same pipeline occurrence, or None if
    critique_plan was unparseable or this length has no k configured.
    llm_response is the full raw text of the critique LLM call.
    """
    config = state["config"]
    target_file_location = state["target_file_location"]
    ground_truth_location = state["ground_truth_location"]
    validation_mode = state.get("validation_mode", "hard_match")

    prompt = _build_critique_prompt(state, script, rag_hints="")
    if not prompt:
        return script, state.get("current_score", 0.0), "Prompt build failed", False, [], None, None, "", None, ""

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
    llm_response = res[0]

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

    # Parse $CONFIDENCE$...$END_CONFIDENCE$ block (this call's self-reported value)
    self_reported_confidence, confidence_raw = _parse_pipeline_confidence(
        res[0], config.logger, tag="_run_critique_llm"
    )
    # Blend into the case-wide pipeline confidence/frequency table -- None if no
    # plan was parsed (nothing to key the occurrence on).
    if critique_plan:
        confidence, occurrences = _record_pipeline_confidence(state, critique_plan, self_reported_confidence)
        credibility_weight = _credibility_weight_from_occurrences(occurrences, state.get("credibility_k"))
    else:
        confidence, occurrences, credibility_weight = None, 0, None
    config.logger.info(
        f"[_run_critique_llm] Confidence: self_reported={confidence_raw!r} "
        f"({self_reported_confidence}) -> blended={confidence}, "
        f"credibility_weight: occurrences={occurrences} -> {credibility_weight}"
    )

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
                    confidence=confidence,
                    column_type_weights=state.get("column_type_weights"),
                    credibility_weight=credibility_weight,
                )
            except Exception:
                new_score = 0.0
                validation_passed = False

    return (
        new_script, new_score, new_response, validation_passed, critique_plan,
        score_components, confidence, confidence_raw, credibility_weight, llm_response,
    )


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

    (
        new_script, new_score, new_response, critique_validation_passed, critique_plan,
        new_score_components, new_confidence, new_confidence_raw, new_credibility_weight, new_llm_response,
    ) = _run_critique_llm(state, state["current_script"])

    _crit_components_str = (
        "components={" + ", ".join(f"{k}={v}" for k, v in new_score_components.items()) + "}"
        if new_score_components else "components=None"
    )
    config.logger.info(
        f"[mcts_critique] Iter {state['iteration']}: "
        f"score {state['current_score']:.4f} → {new_score:.4f}, "
        f"confidence={new_confidence_raw!r} ({new_confidence}), {_crit_components_str}"
    )

    # Build critique_selection_path by walking/creating tree nodes for critique_plan,
    # capped at the expanded node's depth so critique never grows the tree beyond
    # the current expansion frontier.
    # Split merged GROUP_BY/AGGREGATE steps so tree nodes match expand-layer structure.
    expanded_depth: int = len(state.get("rollout_history", []))
    critique_selection_path: List[MCTSNode] = []
    if critique_plan:
        critique_plan = _canonicalize_column_ops(_split_groupby_aggregate(critique_plan))
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
            df_gt = drop_leading_index_col_if_present(df_gt)
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
        "critique_confidence": new_confidence if new_confidence is not None else 0.0,
        "critique_confidence_raw": new_confidence_raw,
        "critique_credibility_weight": new_credibility_weight if new_credibility_weight is not None else 0.0,
        "critique_llm_response": new_llm_response,
        "log_messages": state["log_messages"]
        + [
            f"[CRITIQUE] iter={state['iteration']} "
            f"score_before={state['current_score']:.4f} score_after={new_score:.4f} "
            f"confidence={new_confidence_raw!r} ({new_confidence}) "
            f"credibility_weight={new_credibility_weight} "
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
        "current_confidence": None,
        "current_credibility_weight": None,
        # Clear stale critique state from previous iterations
        "critique_selection_path": [],
        "critique_score": 0.0,
        "critique_confidence": 0.0,
        "critique_confidence_raw": "",
        "critique_credibility_weight": 0.0,
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
      - If same_leaf_stopping > 0, also stop once any one leaf's total visit count reaches it.
      - Iteration cap (max_iterations) is ignored.

    Iteration mode (cost_budget == 0, original behavior):
      - Always stop on validation_passed.
      - Stop on score plateau (early_stopping iterations with no improvement).
      - Stop once any one leaf's total visit count reaches same_leaf_stopping (if enabled).
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

    no_improvement_count = state.get("no_improvement_count", 0)
    early_stopping = state.get("early_stopping", 5)
    same_leaf_stopping = state.get("same_leaf_stopping", 0)
    cost_budget = state.get("cost_budget", 0.0)

    # Optional: stop once any single leaf has accumulated this many total visits
    # (not necessarily consecutive) — a sign the search keeps returning to the
    # same plan instead of finding new ones. MCTSNode.visits is the node's
    # all-time visit count, so this is a simple threshold check, not a counter
    # we maintain ourselves.
    _last_leaf = state.get("last_selected_leaf")
    if same_leaf_stopping > 0 and _last_leaf is not None and _last_leaf.visits >= same_leaf_stopping:
        config.logger.info(
            f"[check_budget] Leaf visited {_last_leaf.visits} times total "
            f"(same_leaf_stopping={same_leaf_stopping}) — stopping early."
        )
        return "done"

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
