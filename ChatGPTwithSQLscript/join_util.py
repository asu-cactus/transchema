import os
import re
import glob
import logging

import pandas as pd

# autopipeline-benchmarks/* lives one level up from this file's repo root
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Benchmark -> on-disk pipelines root. "autopipeline" is the original
# github-pipelines benchmark this file was written for; "smart_building" is
# the 50/50 test/training split built from the smart_building.zip benchmark
# (see autopipeline-benchmarks/smartbuilding-pipelines-split/), each case
# scripted+validated by hand against compare_tables() before being wired in
# here (see smartbuilding_solved_scripts/ and smartbuilding_solutions_manifest.csv).
PIPELINE_ROOTS = {
    "autopipeline": os.path.join(_REPO_ROOT, "autopipeline-benchmarks", "github-pipelines"),
    "smart_building": os.path.join(_REPO_ROOT, "autopipeline-benchmarks", "smartbuilding-pipelines-split"),
    "smart_building_v2": os.path.join(_REPO_ROOT, "autopipeline-benchmarks", "smartbuilding-pipelines-v2-split"),
}

# COPY needs the CSV's leading unnamed pandas-index column stripped out (it isn't
# part of any declared table schema); cache the stripped copies so repeat runs
# don't re-process multi-MB files every time.
_CLEAN_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".autopipeline_cache")


def convert_target_names(target_names_str):
    """'Target6_56' -> 'length6_56' (the on-disk case folder name)."""
    target_names = target_names_str.split(',')
    converted_names = []

    for target_name in target_names:
        match = re.match(r'^Target(\d+)_(\d+)$', target_name.strip())
        if match:
            number1, number2 = match.groups()
            converted_names.append(f"length{number1}_{number2}")
        else:
            converted_names.append(target_name)

    return ', '.join(converted_names)


def case_folder(case_name, benchmark="autopipeline"):
    """case_name is the converted 'lengthN_M' folder name."""
    return os.path.join(PIPELINE_ROOTS[benchmark], case_name)


def num_source_tables(case_name, benchmark="autopipeline"):
    """Count how many test_N.csv files this case has (1 source, up to 11+)."""
    pattern = os.path.join(case_folder(case_name, benchmark), "test_*.csv")
    return len(glob.glob(pattern))


def target_csv_path(case_name, benchmark="autopipeline"):
    return os.path.join(case_folder(case_name, benchmark), "target.csv")


def _drop_leading_index_col_if_present(df):
    """Drop the first column only if it's actually a throwaway pandas index
    column (unnamed, or literally "Unnamed: 0") -- true for every github-pipelines
    CSV, but NOT true for smart_building's CSVs, whose first column is real data
    (e.g. CST/date). Blindly doing index_col=0 there would silently drop a real
    column and corrupt every row (this exact bug was already hit and fixed for
    the pandas/single-step-cot pipeline; see util/utils.py's
    drop_leading_index_col_if_present, which this mirrors for the same reason)."""
    if len(df.columns) > 0:
        first_col = str(df.columns[0])
        if first_col == "" or first_col.startswith("Unnamed:"):
            return df.drop(columns=df.columns[0])
    return df


def clean_source_csv_path(case_name, source_idx, benchmark="autopipeline"):
    """Return a cached, index-column-free copy of test_{source_idx}.csv, creating it on first use.

    Postgres COPY maps columns positionally, so the raw CSV's leading unnamed
    index column (pandas' default row index) would misalign every column against
    a table created from the declared (index-free) schema. We strip it once here
    instead of asking the LLM to work around it in SQL. For smart_building, the
    first column is real data (not a throwaway index), so nothing is dropped.
    """
    raw_path = os.path.join(case_folder(case_name, benchmark), f"test_{source_idx}.csv")
    cache_dir = os.path.join(_CLEAN_CACHE_DIR, benchmark, case_name)
    clean_path = os.path.join(cache_dir, f"test_{source_idx}.csv")

    if os.path.exists(clean_path) and os.path.getmtime(clean_path) >= os.path.getmtime(raw_path):
        return clean_path

    os.makedirs(cache_dir, exist_ok=True)
    df = pd.read_csv(raw_path)
    df = _drop_leading_index_col_if_present(df)
    df.to_csv(clean_path, index=False)
    logging.info(f"Cleaned {raw_path} -> {clean_path} ({len(df)} rows)")
    return clean_path


def read_target_dataframe(case_name, benchmark="autopipeline"):
    """Full ground-truth target table, index column dropped (only if it's actually
    a throwaway index column -- see _drop_leading_index_col_if_present)."""
    df = pd.read_csv(target_csv_path(case_name, benchmark))
    return _drop_leading_index_col_if_present(df)
