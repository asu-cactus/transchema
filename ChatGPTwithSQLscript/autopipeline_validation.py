"""Optional alternate validation for auto_pipeline_join.py, using the same
compare_lists_matching / compare_tables_matching functions that
Langraph/mcts_search.py uses to score the MCTS/pandas pipeline (via its
--validation_method flag). This lets the SQL baseline be scored with the
same methodology, for a fair comparison, without touching join.py's
existing validation() (that one stays exactly as-is).

Loading these is a bit delicate: validation/hard_match.py does
`from util.utils import are_elements_equal`, expecting the repo-root `util/`
*package*. But ChatGPTwithSQLscript already has its own flat `util.py`
module, and Python caches whichever "util" gets imported first under that
same bare name in sys.modules — so importing both naively in one process
means one of them silently shadows the other. We load the repo-root
`validation.hard_match` chain first (with our own `util` binding
temporarily popped out of sys.modules), grab the two functions we need,
then restore our own util.py binding so the rest of this codebase is
unaffected.
"""
import os
import sys
import importlib

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_hard_match():
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)

    saved_util = sys.modules.pop("util", None)
    try:
        hard_match = importlib.import_module("validation.hard_match")
    finally:
        if saved_util is not None:
            sys.modules["util"] = saved_util
        else:
            sys.modules.pop("util", None)

    return hard_match.compare_lists_matching, hard_match.compare_tables_matching


compare_lists_matching, compare_tables_matching = _load_hard_match()


def validate_autopipeline_style(sql_result_df, target_df, method="hard_match"):
    """method:
      - "hard_match": compare_lists_matching — per-column partial credit, matches
        columns by NAME.
      - "autopipeline": compare_tables_matching — binary (all-or-nothing), matches
        columns by DATA CONTENT (robust to naming/casing).

    Returns (accuracy, is_correct, similarity_scores, matched_or_error_info) —
    same 4-tuple shape as join.validation(), for drop-in use in run_case.
    """
    if method == "hard_match":
        # compare_lists_matching requires exact column-name matches, but Postgres
        # lowercases unquoted identifiers — realign generated columns to the
        # target's original casing first (a SQL-path artifact, not something the
        # shared validation code should need to know about).
        target_cols_by_lower = {c.lower(): c for c in target_df.columns}
        rename = {
            c: target_cols_by_lower[c.lower()]
            for c in sql_result_df.columns
            if c not in target_df.columns and c.lower() in target_cols_by_lower
        }
        sql_result_df = sql_result_df.rename(columns=rename)
        return compare_lists_matching(sql_result_df, target_df)
    elif method == "autopipeline":
        return compare_tables_matching(sql_result_df, target_df)
    else:
        raise ValueError(f"Unknown validation method: {method!r} (use 'hard_match' or 'autopipeline')")
