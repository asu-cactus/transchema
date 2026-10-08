"""Value-based det_score for the critique_data.py experiments (CoT, Chain-of-Operators,
and their +Critique variants).

Same calibrated formula mcts_search.py uses -- the per-length `top` component weights
and per-column-type sub-metric weights from get_length_score_weights() -- MINUS the
pipeline-frequency `credibility_weight` component, which has no meaning outside a tree
search (it is derived from how often a pipeline recurs across MCTS rollouts).

Dropping it needs no formula change: value_based_relative_csv_score builds its score_1
component dict from whatever is non-None, and _weighted_avg_available renormalizes the
remaining weights. Passing credibility_weight=None therefore yields the same formula
over the remaining components.

This module deliberately does NOT touch eval_score_value_based.py. It calls the existing
value_based_relative_csv_score() -- which already accepts every parameter needed -- so
the calibrated scorer and everything mcts_search.py depends on stay byte-identical. The
only thing reimplemented here is the child-process timeout wrapper, because
value_based_relative_csv_score_timed() does not forward weights/confidence.
"""

import multiprocessing

from eval_score_value_based import (
    get_length_score_weights,
    value_based_relative_csv_score,
)

# eval_score_value_based.SCORE_TIMEOUT is 60s, which proved too tight here: 6 of 100 L1
# cases per arm blew it and recorded a FAKE score of 0.0 (the exception is caught and
# score stays 0), which is indistinguishable from a genuinely worthless output and
# silently sinks those attempts in any score-based selection. Overridden locally rather
# than by editing eval_score_value_based.py, which mcts_search.py depends on.
COT_SCORE_TIMEOUT = 150

_WEIGHT_CACHE = {}


def get_case_score_weights(length):
    """(top_weights, column_type_weights) for `length`.

    Same call mcts_search.py makes; the third element (credibility smoothing
    constant k) is deliberately discarded -- credibility is excluded here.
    Falls back to the pooled all-length weights for an unknown length.
    """
    if length not in _WEIGHT_CACHE:
        try:
            top, column_type_weights, _k = get_length_score_weights(length)
        except Exception:
            top, column_type_weights = None, None
        _WEIGHT_CACHE[length] = (top, column_type_weights)
    return _WEIGHT_CACHE[length]


def _score_worker(df_gen, df_gt, precomputed_gt, weights, column_type_weights,
                  confidence, result_queue):
    """Subprocess target: score and put the 6-tuple in the queue (None on failure)."""
    try:
        result_queue.put(
            value_based_relative_csv_score(
                df_gen,
                df_gt,
                precomputed_gt=precomputed_gt,
                weights=weights,
                confidence=confidence,
                column_type_weights=column_type_weights,
                credibility_weight=None,  # pipeline-frequency term excluded
            )
        )
    except Exception:
        result_queue.put(None)


def cot_value_based_score(df_gen, df_gt, length=None, confidence=None,
                          timeout=COT_SCORE_TIMEOUT, precomputed_gt=None):
    """Score `df_gen` against `df_gt` with the per-length calibrated weights,
    excluding the credibility component.

    length:     pipeline length, selects the calibrated weights. None -> equal-weight
                defaults (the previous behaviour of these experiments).
    confidence: self-reported LLM confidence in [0, 1] from the $CONFIDENCE$ block,
                or None when the model did not emit one -- in which case the
                component is renormalized away rather than counted as zero.

    Returns the same 6-tuple as value_based_relative_csv_score. Raises TimeoutError
    if scoring exceeds `timeout`, matching value_based_relative_csv_score_timed.
    """
    weights, column_type_weights = get_case_score_weights(length)

    queue = multiprocessing.Queue()
    # NOT a daemon: value_based_relative_csv_score -> relative_csv_score runs the FD tool
    # in its own child process (eval_score/score.py), and a daemon may not have children.
    # Orphaning is handled by critique_data.py instead, which runs each case worker in
    # its own process group and kills the whole group on timeout.
    proc = multiprocessing.Process(
        target=_score_worker,
        args=(df_gen, df_gt, precomputed_gt, weights, column_type_weights,
              confidence, queue),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        raise TimeoutError(f"cot_value_based_score timed out after {timeout}s")

    try:
        result = queue.get_nowait()
    except Exception:
        result = None
    if result is None:
        raise RuntimeError("cot_value_based_score failed in subprocess")
    return result
