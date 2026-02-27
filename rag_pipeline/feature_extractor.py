"""
Feature extractor for RAG retrieval: computes a fixed 23-dim structural vector
per transformation case. Used for feature-based retrieval alongside or instead of text embedding.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Optional, Tuple, Union

import pandas as pd

FEATURE_DIM = 23
OPERATOR_BINS = ["groupby", "merge", "union", "pivot", "unpivot", "other"]
OPERATOR_ALIASES = {"concat": "union"}
# Map multi_step operation names (from critique operation_history) to OPERATOR_BINS
OPERATION_HISTORY_TO_BIN = {
    "join": "merge",
    "group_by/aggregate": "groupby",
    "groupby": "groupby",
    "union": "union",
    "concat": "union",
    "pivot": "pivot",
    "unpivot": "unpivot",
}
TYPE_BINS = ["int", "float", "str", "datetime", "bool"]


def _dtype_to_bin(dtype_str: str) -> str:
    s = (dtype_str or "").lower()
    if "datetime" in s or "timestamp" in s:
        return "datetime"
    if "bool" in s:
        return "bool"
    if "float" in s:
        return "float"
    if s.startswith("int") or s.startswith("uint") or "int" in s:
        return "int"
    return "str"


def _count_column_types(df: pd.DataFrame) -> List[int]:
    counts = {t: 0 for t in TYPE_BINS}
    for col in df.columns:
        kind = _dtype_to_bin(str(df[col].dtype))
        counts[kind] = counts.get(kind, 0) + 1
    return [counts[t] for t in TYPE_BINS]


def _operator_histogram(operator_list: List[str]) -> List[int]:
    hist = {op: 0 for op in OPERATOR_BINS}
    for name in operator_list or []:
        op = (name or "").strip().lower()
        op = OPERATOR_ALIASES.get(op, op)
        if op in hist:
            hist[op] += 1
        else:
            hist["other"] += 1
    return [hist[op] for op in OPERATOR_BINS]


def _parse_operator_pipeline(content: str) -> List[str]:
    content = (content or "").strip()
    if not content:
        return []
    try:
        parsed = ast.literal_eval(content)
        return [str(x) for x in parsed] if isinstance(parsed, list) else []
    except Exception:
        return []


def parse_operation_history_for_query(
    operation_history: Optional[Union[str, list]],
) -> List[str]:
    """
    Parse operation_history from the critique flow (failed pipeline) into a list of
    operator names suitable for compute_from_data(..., pipeline_operator_list=...).

    operation_history is typically the string form of a list, e.g. from ms_info[-1]:
      "['JOIN : [\"col1\", \"col2\"]', 'GROUP_BY/AGGREGATE', 'UNION : [\"t1\", \"t2\"]']"
    Each element may be "OP" or "OP : ...". We take the part before " : " and map
    multi_step names (JOIN, GROUP_BY/AGGREGATE, UNION, PIVOT, UNPIVOT) to
    OPERATOR_BINS (merge, groupby, union, pivot, unpivot, other).

    Returns:
        List of operator names (e.g. ["merge", "groupby", "union"]) for the histogram.
    """
    if operation_history is None:
        return []
    raw_list: List[str] = []
    if isinstance(operation_history, list):
        raw_list = [str(x) for x in operation_history]
    elif isinstance(operation_history, str):
        s = operation_history.strip()
        if not s:
            return []
        try:
            parsed = ast.literal_eval(s)
            raw_list = [str(x) for x in parsed] if isinstance(parsed, list) else []
        except Exception:
            return []
    else:
        return []
    result: List[str] = []
    for item in raw_list:
        item = (item or "").strip()
        if not item:
            continue
        # Take prefix before " : " (e.g. "JOIN : [...]" -> "JOIN")
        if " : " in item:
            op_raw = item.split(" : ", 1)[0].strip()
        else:
            op_raw = item
        op_lower = op_raw.lower()
        full_lower = item.lower()  # use full item for fallback (e.g. "group_by" = ..., "aggregations" = ...)
        mapped = OPERATION_HISTORY_TO_BIN.get(op_lower)
        if mapped is None:
            # GROUP_BY/AGGREGATE may appear as prefix or in full string (e.g. "aggregations")
            if ("group" in full_lower and "aggregate" in full_lower) or (
                "group" in full_lower and "aggregations" in full_lower
            ):
                mapped = "groupby"
            elif "join" in full_lower:
                mapped = "merge"
            elif "union" in full_lower or "concat" in full_lower:
                mapped = "union"
            elif "pivot" in full_lower:
                mapped = "pivot"
            elif "unpivot" in full_lower:
                mapped = "unpivot"
            elif "no_more_operation" in full_lower or not op_raw:
                continue  # skip sentinel / empty
            else:
                mapped = "other"
        result.append(mapped)
    return result


def _schema_overlap(source_column_sets: List[set], target_columns: List[str]) -> float:
    if not target_columns:
        return 0.0
    all_src = set().union(*source_column_sets) if source_column_sets else set()
    target_set = set(c.strip() for c in target_columns if c)
    return len(target_set & all_src) / len(target_set) if target_set else 0.0


def _avg_uniqueness_ratio(df: pd.DataFrame, max_rows: int = 50_000) -> float:
    if df is None or df.empty or len(df.columns) == 0:
        return 0.0
    sample = df.head(max_rows) if len(df) > max_rows else df
    nrows = len(sample)
    if nrows == 0:
        return 0.0
    ratios = []
    for col in sample.columns:
        try:
            ratios.append(sample[col].nunique() / nrows)
        except Exception:
            pass
    return sum(ratios) / len(ratios) if ratios else 0.0


def compute_from_case_folder(case_folder: Path) -> Tuple[List[float], Optional[str]]:
    """
    Compute 23-dim feature vector from a case folder under rag-examples-w-pipeline.

    Expects:
      - case_folder/Source_datasets/*.csv (e.g. test_*.csv)
      - case_folder/Target_datasets/target.csv
      - case_folder/operator_pipeline.txt (optional)

    Returns:
      (vector, case_id) e.g. ("4_24" from folder "Length4_24"). case_id is None if folder name does not start with "Length".
    """
    case_folder = Path(case_folder)
    folder_name = case_folder.name
    case_id = folder_name.replace("Length", "") if folder_name.startswith("Length") else None

    src_dir = case_folder / "Source_datasets"
    if not src_dir.is_dir():
        src_dir = case_folder
    src_files = sorted(src_dir.glob("test_*.csv")) or sorted(src_dir.glob("*.csv"))
    source_dfs: List[pd.DataFrame] = []
    for fp in src_files:
        try:
            df = pd.read_csv(fp, low_memory=False, nrows=100_000)
            df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
            source_dfs.append(df)
        except Exception:
            continue

    tgt_dir = case_folder / "Target_datasets"
    tgt_file = (tgt_dir / "target.csv") if tgt_dir.is_dir() else (case_folder / "target.csv")
    target_df: Optional[pd.DataFrame] = None
    if tgt_file.exists():
        try:
            target_df = pd.read_csv(tgt_file, low_memory=False, nrows=100_000)
            target_df = target_df.loc[:, ~target_df.columns.str.contains("^Unnamed", na=False)]
        except Exception:
            pass

    operator_list: List[str] = []
    pipeline_path = case_folder / "operator_pipeline.txt"
    if pipeline_path.exists():
        try:
            operator_list = _parse_operator_pipeline(
                pipeline_path.read_text(encoding="utf-8", errors="ignore")
            )
        except Exception:
            pass

    vector = compute_from_data(source_dfs, target_df, operator_list)
    return vector, case_id


def compute_from_data(
    source_dfs: List[pd.DataFrame],
    target_df: Optional[pd.DataFrame],
    pipeline_operator_list: Optional[List[str]] = None,
) -> List[float]:
    """
    Compute 23-dim vector from in-memory source/target data and optional pipeline list.

    Used at ingest (from case folder CSVs) and at query time (from current task data).
    When pipeline is unknown (e.g. query), pass pipeline_operator_list=None.
    """
    num_input_tables = len(source_dfs)
    num_input_cols = sum(df.shape[1] for df in source_dfs) if source_dfs else 0
    total_rows = sum(len(df) for df in source_dfs) if source_dfs else 0
    avg_rows = total_rows / len(source_dfs) if source_dfs else 0.0

    num_output_cols = (
        target_df.shape[1] if target_df is not None and not target_df.empty else 0
    )

    type_counts_in = [0, 0, 0, 0, 0]
    for df in source_dfs:
        for i, c in enumerate(_count_column_types(df)):
            type_counts_in[i] += c

    type_counts_out = (
        _count_column_types(target_df)
        if target_df is not None and not target_df.empty
        else [0, 0, 0, 0, 0]
    )

    op_hist = _operator_histogram(pipeline_operator_list or [])
    pipeline_length = len(pipeline_operator_list) if pipeline_operator_list else 0

    src_col_sets = [set(c.strip() for c in df.columns) for df in source_dfs]
    tgt_cols = list(target_df.columns) if target_df is not None else []
    overlap = _schema_overlap(src_col_sets, tgt_cols)

    uniqueness_ratios = [_avg_uniqueness_ratio(df) for df in source_dfs]
    avg_uniqueness = (
        sum(uniqueness_ratios) / len(uniqueness_ratios) if uniqueness_ratios else 0.0
    )

    vec = (
        [float(num_input_tables), float(num_input_cols), avg_rows]
        + [float(num_output_cols)]
        + [float(x) for x in type_counts_in]
        + [float(x) for x in type_counts_out]
        + [float(x) for x in op_hist]
        + [overlap, avg_uniqueness, float(pipeline_length)]
    )
    assert len(vec) == FEATURE_DIM, f"expected {FEATURE_DIM} dims, got {len(vec)}"
    return vec


def load_source_target_from_folder(folder_path: Path) -> Tuple[List[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Load source CSVs (test_*.csv) and target (target.csv) from a case folder.
    Used at query time to compute the current task's feature vector.
    folder_path: e.g. Path("autopipeline-benchmarks/github-pipelines/length4_24")
    """
    folder_path = Path(folder_path)
    source_dfs = []
    for fp in sorted(folder_path.glob("test_*.csv")):
        try:
            df = pd.read_csv(fp, low_memory=False, nrows=100_000)
            df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
            source_dfs.append(df)
        except Exception:
            continue
    target_df = None
    tgt = folder_path / "target.csv"
    if tgt.exists():
        try:
            target_df = pd.read_csv(tgt, low_memory=False, nrows=100_000)
            target_df = target_df.loc[:, ~target_df.columns.str.contains("^Unnamed", na=False)]
        except Exception:
            pass
    return source_dfs, target_df
