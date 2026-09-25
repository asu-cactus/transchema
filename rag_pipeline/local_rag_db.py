"""
local_rag_db.py — per-case SQLite database for RAG-augmented MCTS simulation.

Lifecycle
---------
  build   (ingest script / external)
          → create_local_rag_db(db_path)
          → insert_case(...) for each retrieved similar case
  query   (Langraph/nodes.py, during MCTS expansion)
          → get_rag_hints(db_path, operation_history) → str injected into prompt
  cleanup (optional, after case finishes)
          → os.unlink(db_path)

Schema
------
Only schema metadata + pipeline steps are stored.  No DataFrames, no CSV rows
beyond the small sample stored in target_examples / source_examples.
folder_path is a disk pointer for on-demand loading if full data is needed later.
"""
from __future__ import annotations

import ast
import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

# Maps MCTS step-string operator prefixes to abstract operator bins.
# Mirrors feature_extractor.OPERATOR_BINS / OPERATION_HISTORY_TO_BIN.
_OP_TO_BIN: Dict[str, str] = {
    "JOIN": "merge",
    "UNION": "union",
    "GROUP_BY/AGGREGATE": "groupby",   # old combined format (RAG DB)
    "GROUP_BY": "groupby",             # split expand layer — key step
    "AGGREGATE": "aggregate",          # split expand layer — agg step
    "PIVOT": "pivot",
    "UNPIVOT": "unpivot",
    "NO_MORE_OPERATION": "terminal",
}

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS local_context (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id             TEXT    NOT NULL,
    folder_path         TEXT    NOT NULL,
    schema_sim_score    REAL    DEFAULT 0.0,
    abstract_pipeline   TEXT,   -- JSON array e.g. ["merge", "groupby"]
    full_pipeline_steps TEXT,   -- JSON array of operator step strings
    target_schema       TEXT,   -- column names/types as plain text
    target_examples     TEXT,   -- sample rows as plain text (token-capped by caller)
    source_schemas      TEXT,   -- JSON: {"test_0": "col_a INT, col_b STR", ...}
    source_examples     TEXT,   -- JSON: {"test_0": "row1\\nrow2\\n...", ...}
    feature_vector       TEXT    -- JSON array of floats (z-scored + L2-normalized), or NULL
)
"""

_CREATE_INDEX = (
    "CREATE INDEX IF NOT EXISTS idx_sim ON local_context(schema_sim_score DESC)"
)


# ── DB lifecycle ──────────────────────────────────────────────────────────────


def create_local_rag_db(db_path: str) -> None:
    """Create the SQLite file and table.  Safe to call on an existing file."""
    conn = sqlite3.connect(db_path)
    conn.execute(_CREATE_TABLE)
    conn.execute(_CREATE_INDEX)
    conn.commit()
    conn.close()


def insert_case(
    db_path: str,
    *,
    case_id: str,
    folder_path: str,
    sim_score: float,
    abstract_pipeline: List[str],
    full_pipeline_steps: List[str],
    target_schema: str,
    target_examples: str,
    source_schemas: Dict[str, str],
    source_examples: Dict[str, str],
    feature_vector: Optional[List[float]] = None,
) -> None:
    """Insert one retrieved case into the local DB.

    Args:
        db_path:             Path to the SQLite file (must already be created).
        case_id:             e.g. "4_24".
        folder_path:         Absolute path to the case folder on disk.
        sim_score:           Schema similarity score from global retrieval (0–1).
        abstract_pipeline:   Operator bins in order, e.g. ["merge", "groupby"].
        full_pipeline_steps: Configured step strings in order, e.g.
                             ["JOIN : [[t0,t1]] COLUMNS=[[...]]", ...].
        target_schema:       Target column names/types as plain text.
        target_examples:     Sample target rows as plain text (caller token-caps).
        source_schemas:      {table_name: "col_a TYPE, col_b TYPE, ..."}.
        source_examples:     {table_name: "row1\\nrow2\\n..."}.
        feature_vector:      Optional structural feature vector (already normalized
                             by the caller), stored as JSON for later cosine-similarity
                             re-ranking in get_rag_hints(). None for modes that don't
                             use feature-vector matching.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO local_context
            (case_id, folder_path, schema_sim_score, abstract_pipeline,
             full_pipeline_steps, target_schema, target_examples,
             source_schemas, source_examples, feature_vector)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            folder_path,
            sim_score,
            json.dumps(abstract_pipeline),
            json.dumps(full_pipeline_steps),
            target_schema,
            target_examples,
            json.dumps(source_schemas),
            json.dumps(source_examples),
            json.dumps(feature_vector) if feature_vector is not None else None,
        ),
    )
    conn.commit()
    conn.close()


# ── DataFrame → text helper ──────────────────────────────────────────────────


def df_to_text(df: "pd.DataFrame", max_rows: int = 3) -> str:
    """Convert a DataFrame sample to a compact string without column truncation.

    Uses pandas option_context so that wide DataFrames never get '...' in the
    middle of columns.  Always call this (instead of df.to_string()) when
    generating text to store in the local RAG DB.
    """
    import pandas as pd  # local import to avoid top-level dependency issues

    sample = df.head(max_rows)
    with pd.option_context(
        "display.max_columns", None,
        "display.width", None,
        "display.max_colwidth", None,
    ):
        return sample.to_string(index=False)


# ── Ground-truth operator mapping ────────────────────────────────────────────

# Maps operator names used in ground_truth_pipelines.csv → MCTS operator strings.
# Operators not in this dict (Date, cat, lower, contain, etc.) are not
# structural MCTS operators and are silently dropped during normalization.
GT_OP_TO_MCTS: Dict[str, str] = {
    "merge":   "JOIN",
    "groupby": "GROUP_BY/AGGREGATE",
    "concat":  "UNION",
    "union":   "UNION",
    "pivot":   "PIVOT",
    "unpivot": "UNPIVOT",
}


def normalize_gt_operators(ops: List[str]) -> List[str]:
    """Map ground-truth CSV operator names to MCTS operator strings.

    Unknown operators (Date, cat, lower, contain, split, …) are dropped because
    they are not modelled by MCTS.  NO_MORE_OPERATION is appended at the end so
    the pipeline terminates correctly in the prefix-matching logic.
    """
    result = []
    for op in ops:
        mcts_op = GT_OP_TO_MCTS.get(op.strip().lower())
        if mcts_op:
            result.append(mcts_op)
    if result:
        result.append("NO_MORE_OPERATION")
    return result


def build_upper_bound_db(
    case_id: str,
    case_folder: "Path",
    gt_csv_path: str,
    db_path: str,
) -> bool:
    """Build a single-entry upper-bound local RAG DB from the ground-truth CSV.

    Looks up the ground-truth operator sequence for *case_id* in *gt_csv_path*,
    maps operator names to MCTS strings, loads source/target DataFrames from
    *case_folder*, and writes a fresh SQLite DB at *db_path*.

    Args:
        case_id:      MCTS case identifier, e.g. "4_35".
        case_folder:  Path to the benchmark folder (contains test_0.csv, …
                      and target.csv).
        gt_csv_path:  Path to ground_truth_pipelines.csv.
        db_path:      Output path for the SQLite file (overwritten if exists).

    Returns:
        True on success; False if case_id is not found in the CSV.
    """
    import pandas as pd
    from rag_pipeline.feature_extractor import load_source_target_from_folder

    target_id = f"Target{case_id}"
    gt_df = pd.read_csv(gt_csv_path, encoding="latin-1")
    rows = gt_df[gt_df["target_id"] == target_id]
    if rows.empty:
        return False

    row = rows.iloc[0]
    # Use full configured pipeline steps when available (curated_pipelines.csv),
    # otherwise fall back to normalizing abstract operator names (ground_truth_pipelines.csv).
    if "pipeline_steps" in row.index and pd.notna(row["pipeline_steps"]) and row["pipeline_steps"]:
        mcts_steps = json.loads(row["pipeline_steps"])
    else:
        raw_ops: List[str] = ast.literal_eval(row["operators"])
        mcts_steps = normalize_gt_operators(raw_ops)
    abstract = [step_to_abstract(s) for s in mcts_steps]

    case_folder = Path(case_folder)
    source_dfs, target_df = load_source_target_from_folder(case_folder)
    if target_df is None:
        return False

    source_schemas = {
        f"test_{i}": ", ".join(f"{col} {dtype}" for col, dtype in zip(df.columns, df.dtypes))
        for i, df in enumerate(source_dfs)
    }
    source_examples = {f"test_{i}": df_to_text(df) for i, df in enumerate(source_dfs)}
    target_schema = ", ".join(
        f"{col} {dtype}" for col, dtype in zip(target_df.columns, target_df.dtypes)
    )
    target_examples = df_to_text(target_df)

    if os.path.exists(db_path):
        os.unlink(db_path)
    create_local_rag_db(db_path)
    insert_case(
        db_path,
        case_id=case_id,
        folder_path=str(case_folder.resolve()),
        sim_score=1.0,
        abstract_pipeline=abstract,
        full_pipeline_steps=mcts_steps,
        target_schema=target_schema,
        target_examples=target_examples,
        source_schemas=source_schemas,
        source_examples=source_examples,
    )
    return True


# ── Global→Local bridge ───────────────────────────────────────────────────────


def populate_from_global_results(db_path: str, global_results: List[Dict]) -> int:
    """Populate a fresh local SQLite DB from the output of GlobalSchemaDB.search().

    Creates the DB at db_path (overwriting any existing file), then inserts one
    row per result.  The schema_sim_score field is taken from result["sim_score"]
    so the local prefix-match query can still rank by similarity.

    Args:
        db_path:        Path for the new SQLite file.
        global_results: List of dicts returned by GlobalSchemaDB.search().
                        Each dict must have: case_id, sim_score, pipeline,
                        target_schema, target_samples, source_schemas,
                        source_samples.

    Returns:
        Number of records inserted.
    """
    if os.path.exists(db_path):
        os.unlink(db_path)
    create_local_rag_db(db_path)

    inserted = 0
    for result in global_results:
        pipeline_text: str = result.get("pipeline", "")
        # Parse full_pipeline_steps from the pipeline string (one step per line,
        # blank lines and terminal are kept so prefix-match logic works correctly)
        full_steps: List[str] = [
            line.strip()
            for line in pipeline_text.splitlines()
            if line.strip()
        ]
        abstract = [step_to_abstract(s) for s in full_steps]

        source_schemas: Dict[str, str] = result.get("source_schemas", {})
        source_samples: Dict[str, str] = result.get("source_samples", {})

        insert_case(
            db_path,
            case_id=str(result.get("case_id", "unknown")),
            folder_path="",
            sim_score=float(result.get("sim_score", 0.0)),
            abstract_pipeline=abstract,
            full_pipeline_steps=full_steps,
            target_schema=result.get("target_schema", ""),
            target_examples=result.get("target_samples", ""),
            source_schemas=source_schemas,
            source_examples=source_samples,
        )
        inserted += 1

    return inserted


# ── Abstract-operator helpers ─────────────────────────────────────────────────


def step_to_abstract(step: str) -> str:
    """Map one configured MCTS step string to its abstract operator bin.

    Examples
    --------
    "JOIN : [[T0, T1]] COLUMNS=..."  → "merge"
    "GROUP_BY/AGGREGATE : ..."       → "groupby"
    "NO_MORE_OPERATION"              → "terminal"
    "UNION : [T0, T1]"              → "union"
    """
    prefix = step.split(":")[0].strip().upper()
    return _OP_TO_BIN.get(prefix, "other")


def operation_history_to_abstract(history: List[str]) -> List[str]:
    """Convert a list of configured MCTS steps to abstract operator bins."""
    return [step_to_abstract(s) for s in history]


# ── Flexible prefix matcher ───────────────────────────────────────────────────


def _flexible_prefix_match(
    current_abstract: List[str],
    rag_abstract: List[str],
) -> Optional[int]:
    """Match current_abstract (MCTS history) against a prefix of rag_abstract.

    Two flex rules handle structural mismatches between MCTS and RAG pipelines:

    Rule 1 — Union collapse
        One MCTS "union" matches one OR MORE consecutive RAG "union" bins.
        Rationale: a single MCTS UNION stacks N tables in one call, while the
        equivalent RAG pipeline may chain N-1 separate pd.concat steps.

    Rule 2 — GroupBy merge
        MCTS ("groupby", "aggregate") matches one RAG "groupby".
        Rationale: the RAG DB stores GROUP_BY/AGGREGATE as a single step, but
        the MCTS expand layer splits it into separate GROUP_BY and AGGREGATE nodes.

    Returns the index of the first unmatched step in rag_abstract (i.e., the
    position of the NEXT operation after the matched prefix), or None if the
    prefix does not match.
    """
    ci = 0  # cursor into current_abstract
    ri = 0  # cursor into rag_abstract

    while ci < len(current_abstract):
        if ri >= len(rag_abstract):
            return None

        c_op = current_abstract[ci]
        r_op = rag_abstract[ri]

        if c_op == r_op:
            ci += 1
            ri += 1
            # Rule 1: consume any extra consecutive RAG unions matched by one MCTS union
            if c_op == "union":
                while ri < len(rag_abstract) and rag_abstract[ri] == "union":
                    ri += 1
        elif (
            c_op == "groupby"
            and r_op == "groupby"
            and ci + 1 < len(current_abstract)
            and current_abstract[ci + 1] == "aggregate"
        ):
            # Rule 2: MCTS (groupby, aggregate) pair → single RAG groupby
            ci += 2
            ri += 1
        else:
            return None  # genuine mismatch

    # All of current_abstract matched — return position of next RAG step
    return ri if ri < len(rag_abstract) else None


# ── Feature-vector similarity ─────────────────────────────────────────────────


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two equal-length vectors. 0.0 if either is empty/zero."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Hint query ────────────────────────────────────────────────────────────────


def get_rag_hints(
    db_path: str,
    operation_history: List[str],
    top_k: int = 3,
    query_vector: Optional[List[float]] = None,
) -> str:
    """Return a formatted hint block for the mcts_expand prompt.

    Queries the local SQLite DB for cases whose abstract_pipeline shares the
    same prefix as operation_history.  From each matched case the *next*
    operation (depth + 1) is extracted and formatted as a few-shot example.

    Args:
        db_path:           Path to the per-case SQLite DB.
        operation_history: The MCTS path so far (configured step strings).
        top_k:             Maximum number of matched examples to include.
        query_vector:       Optional normalized structural feature vector for the
                            current task. When given, ALL prefix matches are
                            collected first and re-ranked by cosine similarity
                            against each row's stored feature_vector (rows without
                            one sort last), instead of taking the first top_k in
                            schema_sim_score order. None preserves prior behavior.

    Returns:
        A multi-line string ready for direct injection into the mcts_expand
        prompt, or "" if db_path is empty / missing / no matches found.
    """
    if not db_path or not os.path.exists(db_path):
        return ""

    current_abstract = operation_history_to_abstract(operation_history)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    all_rows = conn.execute(
        "SELECT * FROM local_context ORDER BY schema_sim_score DESC"
    ).fetchall()
    conn.close()

    # matched is a list of (row, next_idx) where next_idx is the position of
    # the next step in the RAG pipeline's abstract sequence after the matched prefix.
    matched: List[tuple] = []
    for row in all_rows:
        abstract = json.loads(row["abstract_pipeline"] or "[]")
        next_idx = _flexible_prefix_match(current_abstract, abstract)
        if next_idx is not None:
            matched.append((row, next_idx))
        if query_vector is None and len(matched) >= top_k:
            break

    if query_vector is not None and matched:
        def _sim_key(item: tuple) -> float:
            row = item[0]
            raw_fv = row["feature_vector"]
            if not raw_fv:
                return -1.0  # no stored vector -> sorts last
            return _cosine_similarity(query_vector, json.loads(raw_fv))

        matched.sort(key=_sim_key, reverse=True)
        matched = matched[:top_k]

    if not matched:
        return ""

    lines: List[str] = [
        "══════════════════════════════════════════════════════",
        "SIMILAR CASE EXAMPLES (retrieved from similar transformations)",
        "══════════════════════════════════════════════════════",
        "The following examples come from similar transformation cases whose",
        "pipeline prefix matches your current operation history.",
        "IMPORTANT: These are illustrative examples only — NOT exact pipelines to copy.",
        "The source table schemas, column names, and value patterns will differ from",
        "your current task. Use them to understand what kind of operation typically",
        "comes next, but always derive the exact operator configuration (join keys,",
        "group-by columns, aggregations, table order) from the actual source and",
        "target schemas of YOUR current task, not from these examples.",
        "",
    ]

    for i, (row, next_idx) in enumerate(matched, 1):
        steps: List[str] = json.loads(row["full_pipeline_steps"] or "[]")
        source_schemas: Dict[str, str] = json.loads(row["source_schemas"] or "{}")
        source_examples: Dict[str, str] = json.loads(row["source_examples"] or "{}")

        lines.append(f"--- Example {i} (case {row['case_id']}) ---")

        for tbl, schema_text in source_schemas.items():
            lines.append(f"  Source {tbl} schema: {schema_text}")
            if source_examples.get(tbl):
                lines.append(f"  Source {tbl} examples:\n{source_examples[tbl]}")

        lines.append(f"  Target schema: {row['target_schema']}")
        if row["target_examples"]:
            lines.append(f"  Target examples:\n{row['target_examples']}")

        lines.append("  Full pipeline:")
        for j, step in enumerate(steps):
            if j < next_idx:
                lines.append(f"    {j+1}. {step}  [done]")
            elif j == next_idx:
                lines.append(f"    {j+1}. {step}  <<<< NEXT")
            else:
                lines.append(f"    {j+1}. {step}")
        lines.append("")

    return "\n".join(lines)
