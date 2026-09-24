"""Rule-engine JOIN / GROUP_BY hints for the critique_data.py experiments.

The MCTS arm ranks statistical JOIN and GROUP_BY candidates and seeds its tree with the
top 3 of each (_RULE_INJECT_TOP_K, Langraph/nodes.py). This module reproduces that
ranking so the CoT / Chain-of-Operators arms can be given the same evidence in their
prompts, making the two arms comparable.

Ranking is done ONCE PER CASE at depth 0 -- an empty current schema, exactly the vantage
point MCTS uses at its root. MCTS re-ranks at every node against the real partial
pipeline, which costs an LLM call plus a script execution per ranking; doing that here
would inflate the very token counts these experiments measure. Consequences:

  * JOIN  -- depth 0 IS the right vantage point for the first join; scores are exact.
  * GROUP_BY -- combined_dvr_delta needs an intermediate table, and at depth 0 there is
    none, so it falls back to the sole source table (single-source cases: exact) or the
    best-overlapping source table (multi-source: an approximation).

The scoring formulas mirror Langraph/nodes.py::_rank_join_v3_candidates and
::_rank_groupby_v3_candidates. They are reimplemented rather than imported because
Langraph/nodes.py imports auto_suggest_llm_util, which would make the import circular,
and because nothing reachable from mcts_search.py may be modified. Everything the
formulas are built from is REUSED from hints/hint_v3.py, which is not modified.

Verified against real MCTS logs -- the first "rule engine proposed" line in a case's log
is its depth-0 ranking:

    length3_2  JOIN      0.952 / 0.905 / 0.730
    length3_49 GROUP_BY  title 0.824, amazon_product_url 0.300
"""

import os
import re
import signal
from contextlib import contextmanager
from itertools import combinations

import pandas as pd

import hints.hint_v3 as hint_v3

# Mirrors Langraph/nodes.py
RULE_HINT_TOP_K = 3           # _RULE_INJECT_TOP_K
_GROUPBY_COMBO_TOP_N = 5      # _GROUPBY_COMBO_TOP_N
_GROUPBY_COMBO_MAX_SIZE = 2   # _GROUPBY_COMBO_MAX_SIZE

# Mirrors the 30s subprocess budget mcts_search.py gives each static precompute. Used
# here via SIGALRM instead of a child process so the guard does not depend on whether
# the calling process is daemonic.
_COMPUTE_TIMEOUT_SECONDS = 30

# Keyed by (directory, len_idx_target_idx); both precomputes are expensive
# (all pairwise column combinations for JOIN, the FD tool for GROUP BY) and the result
# is constant for a case.
_CASE_CACHE = {}


class _RuleHintTimeout(Exception):
    pass


def _split_table_names(source_data_name_list, data_split):
    """Table names that make hint_v3.load_tables read the requested split.

    load_tables maps a name starting with "Source" to test_{i}.csv unconditionally, so
    under --data_split training the hints would be derived from TEST data while the
    model only ever sees training data. Its else-branch uses the name verbatim as the
    filename, so passing "training_0" reads training_0.csv.

    Returns (names_for_loading, display_map) where display_map turns the loading names
    back into the Source{case}_{i} names the prompts use. For the test split the names
    are unchanged and the map is empty.
    """
    if data_split == "test":
        return list(source_data_name_list), {}
    loading = [f"{data_split}_{i}" for i in range(len(source_data_name_list))]
    return loading, dict(zip(loading, source_data_name_list))


def _restore_display_names(ranked, display_map):
    """Rewrite loading names back to Source names inside candidate config strings.

    Longest-first so training_1 cannot be rewritten by a training_10 prefix, and
    \\b-anchored so only whole names are replaced.
    """
    if not display_map:
        return ranked
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in sorted(display_map, key=len, reverse=True)) + r")\b"
    )
    return [
        (pattern.sub(lambda m: display_map[m.group(0)], cfg), score)
        for cfg, score in ranked
    ]


@contextmanager
def _time_limit(seconds):
    """Hard wall-clock limit via SIGALRM. No-op if not on the main thread (SIGALRM can
    only be armed there), in which case the caller simply runs unbounded."""
    def _handler(signum, frame):
        raise _RuleHintTimeout()

    try:
        previous = signal.signal(signal.SIGALRM, _handler)
    except ValueError:
        yield  # not the main thread — run without the guard
        return

    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _rank_join(join_static):
    """Depth-0 JOIN ranking: (evidence + name_score + necessity) / 3.

    At depth 0 the current schema is empty, so a candidate's "new columns" are simply
    both tables' columns and necessity is the share of ALL target columns they cover.
    """
    candidates = join_static.get("candidates") or []
    source_columns = join_static.get("source_columns") or {}
    target_columns = join_static.get("target_columns")
    if not candidates or not source_columns or target_columns is None:
        return []

    current_schema = set()  # depth 0: nothing built yet
    scored = []
    for cand in candidates:
        t1, c1, t2, c2 = cand["t1"], cand["c1"], cand["t2"], cand["c2"]
        new_cols = (
            set(source_columns.get(t1, [])) | set(source_columns.get(t2, []))
        ) - current_schema
        necessity = hint_v3.necessity(new_cols, current_schema, target_columns)
        score = (cand["evidence"] + cand["name_score"] + necessity) / 3.0
        cfg = f"JOIN : [[{t1}, {t2}]] columns=[[{t1}.{c1}, {t2}.{c2}]]"
        scored.append((cfg, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def _resolve_depth0_table(groupby_static, source_data_name_list, directory,
                          len_idx_target_idx):
    """Depth-0 stand-in for the intermediate table: the sole source table, else the
    source table overlapping the target most (hint_v3.best_overlapping_table)."""
    try:
        tables = hint_v3.load_tables(directory, source_data_name_list, len_idx_target_idx)
    except Exception:
        return None
    if not tables:
        return None
    if len(tables) == 1:
        return next(iter(tables.values()))
    best = hint_v3.best_overlapping_table(tables, groupby_static.get("target_columns", []))
    return tables.get(best) if best is not None else None


def _rank_groupby(groupby_static, source_data_name_list, directory, len_idx_target_idx):
    """Depth-0 GROUP_BY ranking: (leftness_prior + dvr_delta + fd_score) / 3 over the
    hint_v3 column pool, bounded column combinations, and the target's FD keys."""
    individual_columns = groupby_static.get("individual_columns") or []
    fd_keys = groupby_static.get("fd_keys") or set()
    source_columns = groupby_static.get("source_columns") or {}
    target_columns = groupby_static.get("target_columns") or []
    if not individual_columns or not target_columns:
        return []

    intermediate_df = _resolve_depth0_table(
        groupby_static, source_data_name_list, directory, len_idx_target_idx
    )
    if intermediate_df is None:
        return []

    try:
        target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
        target_df = pd.read_csv(target_file, low_memory=False)
        target_df = target_df.drop(target_df.columns[0], axis=1)
    except Exception:
        return []

    def _score(entries):
        # entries: list of (table, column, leftness, matched_target_col)
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

    scored = []

    # Individual columns — the hint_v3 statistical pool
    for entry in individual_columns:
        s = _score([(entry["t"], entry["c"], entry["leftness"], entry["matched_target_col"])])
        scored.append((f"GROUP_BY : [{entry['t']}.{entry['c']}]", s))

    # Bounded heuristic combinations of the top individual columns
    top_n = sorted(individual_columns, key=lambda e: e["leftness"])[:_GROUPBY_COMBO_TOP_N]
    for combo_size in range(2, _GROUPBY_COMBO_MAX_SIZE + 1):
        for combo in combinations(top_n, combo_size):
            entries = [(e["t"], e["c"], e["leftness"], e["matched_target_col"]) for e in combo]
            cols_str = ", ".join(f"{e['t']}.{e['c']}" for e in combo)
            scored.append((f"GROUP_BY : [{cols_str}]", _score(entries)))

    # FD-discovered determinant sets, resolved back to their source tables
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
        cols_str = ", ".join(f"{t}.{c}" for t, c in resolved)
        scored.append((f"GROUP_BY : [{cols_str}]", _score(entries)))

    # The FD path and the combination path can produce the same column set; keep the
    # first (identical entries score identically either way).
    seen = set()
    deduped = []
    for cfg, s in scored:
        if cfg in seen:
            continue
        seen.add(cfg)
        deduped.append((cfg, s))

    deduped.sort(key=lambda x: x[1], reverse=True)
    return deduped


def compute_case_rule_hints(source_data_name_list, directory, len_idx_target_idx,
                            logger=None, top_k=RULE_HINT_TOP_K, data_split="test"):
    """Top-`top_k` depth-0 JOIN and GROUP_BY rule candidates for one case.

    data_split selects which source CSVs the hints are derived from, so that under
    --data_split training the hints see only training data -- the same data the model
    is given. Candidates are still reported under the Source{case}_{i} names the
    prompts use.

    Returns {"join": [(cfg, score), ...], "group_by": [(cfg, score), ...]}. A key is []
    when its precompute found nothing, timed out, or failed -- callers should simply omit
    that block rather than treat it as an error. Cached per (case, split).
    """
    cache_key = (directory, len_idx_target_idx, data_split)
    if cache_key in _CASE_CACHE:
        return _CASE_CACHE[cache_key]

    load_names, display_map = _split_table_names(source_data_name_list, data_split)

    def _log(message):
        if logger is not None:
            logger.info(message)

    def _warn(message):
        if logger is not None:
            logger.warning(message)

    ranked = {"join": [], "group_by": []}

    try:
        with _time_limit(_COMPUTE_TIMEOUT_SECONDS):
            join_static = hint_v3.compute_join_static_candidates(
                load_names, directory, len_idx_target_idx
            )
        if join_static:
            ranked["join"] = _restore_display_names(
                _rank_join(join_static)[:top_k], display_map
            )
    except _RuleHintTimeout:
        _warn(f"[rule_hints JOIN] Timed out after {_COMPUTE_TIMEOUT_SECONDS}s — skipping")
    except Exception as exc:
        _warn(f"[rule_hints JOIN] Failed, skipping: {exc}")

    try:
        with _time_limit(_COMPUTE_TIMEOUT_SECONDS):
            groupby_static = hint_v3.compute_groupby_static_candidates(
                load_names, directory, len_idx_target_idx
            )
            if groupby_static:
                ranked["group_by"] = _restore_display_names(
                    _rank_groupby(
                        groupby_static, load_names, directory, len_idx_target_idx
                    )[:top_k],
                    display_map,
                )
    except _RuleHintTimeout:
        _warn(f"[rule_hints GROUP_BY] Timed out after {_COMPUTE_TIMEOUT_SECONDS}s — skipping")
    except Exception as exc:
        _warn(f"[rule_hints GROUP_BY] Failed, skipping: {exc}")

    _log(
        f"[rule_hints] top {top_k} JOIN: "
        f"{[(cfg, round(s, 3)) for cfg, s in ranked['join']]}"
    )
    _log(
        f"[rule_hints] top {top_k} GROUP_BY: "
        f"{[(cfg, round(s, 3)) for cfg, s in ranked['group_by']]}"
    )

    _CASE_CACHE[cache_key] = ranked
    return ranked


def format_rule_hints(ranked, kinds=("join", "group_by")):
    """Render ranked candidates as a prompt block. Empty string when there is nothing to
    show, so callers can append unconditionally."""
    if not ranked:
        return ""

    sections = []
    labels = {"join": "Top JOIN candidates", "group_by": "Top GROUP BY candidates"}
    for kind in kinds:
        entries = ranked.get(kind) or []
        if not entries:
            continue
        lines = [f"{labels.get(kind, kind)}:"]
        for i, (cfg, score) in enumerate(entries, start=1):
            lines.append(f"  {i}. {cfg}  (score {score:.2f})")
        sections.append("\n".join(lines))

    if not sections:
        return ""

    return (
        "\n\nRule-based candidates, derived by statistical analysis of the source and "
        "target tables and ranked best-first. Treat them as suggestions, not "
        "instructions — use them only where they fit the transformation:\n"
        + "\n".join(sections)
        + "\n"
    )
