import os
import re
import glob
import logging

import pandas as pd

# autopipeline-benchmarks/github-pipelines lives one level up from this file's repo root
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITHUB_PIPELINES_ROOT = os.path.join(_REPO_ROOT, "autopipeline-benchmarks", "github-pipelines")

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


def case_folder(case_name):
    """case_name is the converted 'lengthN_M' folder name."""
    return os.path.join(GITHUB_PIPELINES_ROOT, case_name)


def num_source_tables(case_name):
    """Count how many test_N.csv files this case has (1 source, up to 11+)."""
    pattern = os.path.join(case_folder(case_name), "test_*.csv")
    return len(glob.glob(pattern))


def target_csv_path(case_name):
    return os.path.join(case_folder(case_name), "target.csv")


def clean_source_csv_path(case_name, source_idx):
    """Return a cached, index-column-free copy of test_{source_idx}.csv, creating it on first use.

    Postgres COPY maps columns positionally, so the raw CSV's leading unnamed
    index column (pandas' default row index) would misalign every column against
    a table created from the declared (index-free) schema. We strip it once here
    instead of asking the LLM to work around it in SQL.
    """
    raw_path = os.path.join(case_folder(case_name), f"test_{source_idx}.csv")
    cache_dir = os.path.join(_CLEAN_CACHE_DIR, case_name)
    clean_path = os.path.join(cache_dir, f"test_{source_idx}.csv")

    if os.path.exists(clean_path) and os.path.getmtime(clean_path) >= os.path.getmtime(raw_path):
        return clean_path

    os.makedirs(cache_dir, exist_ok=True)
    df = pd.read_csv(raw_path, index_col=0)
    df.to_csv(clean_path, index=False)
    logging.info(f"Cleaned {raw_path} -> {clean_path} ({len(df)} rows)")
    return clean_path


def read_target_dataframe(case_name):
    """Full ground-truth target table, index column dropped."""
    return pd.read_csv(target_csv_path(case_name), index_col=0)
