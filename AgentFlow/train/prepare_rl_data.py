"""
Prepares RL training and validation parquet files from the DataMorpher benchmark.

Source: autopipeline-benchmarks/github-pipelines/
Output:
  data/train/datamorphertrain.parquet
  data/val/datamorpherval.parquet

Each example's question is built from the training_N.csv schemas and sample rows.
The test_N.csv paths and target.csv path are stored in extra_info for the rollout
to use at reward-computation time — the model never sees test data in the prompt.

Split: 80% train / 20% val, stratified per length category, seed=42.
"""

import os
import sys
import re
import json
import random
import argparse
from pathlib import Path
from collections import defaultdict

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]          # transchema/
BENCHMARK_DIR = REPO_ROOT / "autopipeline-benchmarks" / "github-pipelines"
OUTPUT_TRAIN = SCRIPT_DIR / "data" / "train" / "datamorphertrain.parquet"
OUTPUT_VAL = SCRIPT_DIR / "data" / "val" / "datamorpherval.parquet"

SAMPLE_ROWS = 5          # number of sample rows shown per source table in the prompt
MAX_COL_WIDTH = 40       # truncate long cell values in the display
RANDOM_SEED = 42
VAL_FRACTION = 0.20


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _truncate_cell(val, max_len: int = MAX_COL_WIDTH) -> str:
    s = str(val)
    return s if len(s) <= max_len else s[:max_len - 3] + "..."


def _format_table_sample(df: pd.DataFrame, table_idx: int, name: str) -> str:
    """Render schema + sample rows as a readable text block."""
    cols = list(df.columns)
    sample = df.head(SAMPLE_ROWS)
    rows_text = []
    for _, row in sample.iterrows():
        cells = " | ".join(_truncate_cell(row[c]) for c in cols)
        rows_text.append(f"  {cells}")
    header = " | ".join(cols)
    return (
        f"[Source Table {table_idx}] (file: {name})\n"
        f"Columns: {', '.join(cols)}\n"
        f"Sample ({min(SAMPLE_ROWS, len(df))} rows):\n"
        f"  {header}\n"
        + "\n".join(rows_text)
    )


def _build_question(example_dir: Path, training_paths: list[Path]) -> str:
    """
    Build the LLM prompt for a given example.

    The prompt shows:
      - Schema + sample rows from every training_N.csv  (derived from training data
        so the model learns what each source table looks like)
      - Target schema hint (column names only from target.csv)
      - Instruction to write a Python/pandas script that reads from
        test_0.csv ... test_N.csv and writes output.csv

    NOTE: test_N.csv paths and target.csv content are NOT shown here —
    they are only used during reward evaluation.
    """
    table_blocks = []
    for i, tp in enumerate(training_paths):
        try:
            df = pd.read_csv(tp, index_col=0, nrows=SAMPLE_ROWS + 1)
        except Exception:
            try:
                df = pd.read_csv(tp, nrows=SAMPLE_ROWS + 1)
            except Exception:
                df = pd.DataFrame()
        table_blocks.append(_format_table_sample(df, i, tp.name))

    target_path = example_dir / "target.csv"
    target_hint = ""
    if target_path.exists():
        try:
            tdf = pd.read_csv(target_path, nrows=1)
            target_hint = (
                "\nTarget output columns (schema hint only, no data shown):\n"
                f"  {', '.join(tdf.columns)}\n"
            )
        except Exception:
            pass

    n = len(training_paths)
    test_file_list = ", ".join(f"test_{i}.csv" for i in range(n))
    tables_text = "\n\n".join(table_blocks)

    prompt = (
        "You are a data transformation expert.\n\n"
        f"You are given {n} source table(s). "
        "Using the schemas and sample rows below (derived from training data), "
        "write a complete Python script using pandas that:\n"
        f"  1. Reads the source tables from: {test_file_list}\n"
        "  2. Applies the necessary joins, filters, aggregations, and type coercions\n"
        "  3. Saves the result to output.csv (index=False)\n\n"
        "The script must be self-contained, import pandas, and work with the exact "
        "column names shown below.\n\n"
        f"{tables_text}\n"
        f"{target_hint}\n"
        "Write ONLY the Python script. Do not include any explanation outside the code."
    )
    return prompt


def _discover_examples(benchmark_dir: Path) -> dict[str, list[Path]]:
    """
    Returns a dict mapping length_category (e.g. 'length1') to a sorted list
    of example directory paths.
    """
    by_length: dict[str, list[Path]] = defaultdict(list)
    pattern = re.compile(r"^(length\d+)_\d+$")
    for entry in sorted(benchmark_dir.iterdir()):
        if entry.is_dir():
            m = pattern.match(entry.name)
            if m:
                by_length[m.group(1)].append(entry)
    return dict(by_length)


def _stratified_split(
    by_length: dict[str, list[Path]],
    val_fraction: float,
    seed: int,
) -> tuple[list[Path], list[Path]]:
    """80/20 split per length category."""
    rng = random.Random(seed)
    train_dirs, val_dirs = [], []
    for length_key in sorted(by_length.keys()):
        dirs = list(by_length[length_key])
        rng.shuffle(dirs)
        n_val = max(1, round(len(dirs) * val_fraction))
        val_dirs.extend(dirs[:n_val])
        train_dirs.extend(dirs[n_val:])
    return train_dirs, val_dirs


def _process_example(example_dir: Path) -> dict | None:
    """
    Process one benchmark example into a record for the parquet dataset.
    Returns None if the directory is missing required files.
    """
    # Discover training CSVs in index order (training_0.csv, training_1.csv, ...)
    training_paths: list[Path] = []
    i = 0
    while True:
        tp = example_dir / f"training_{i}.csv"
        if not tp.exists():
            break
        training_paths.append(tp)
        i += 1

    if not training_paths:
        return None

    # Discover test CSVs (same count as training)
    test_paths: list[Path] = []
    for j in range(len(training_paths)):
        tp = example_dir / f"test_{j}.csv"
        if tp.exists():
            test_paths.append(tp)

    if not test_paths:
        return None

    target_path = example_dir / "target.csv"
    if not target_path.exists():
        return None

    # Parse length and index from directory name e.g. "length4_12"
    m = re.match(r"length(\d+)_(\d+)", example_dir.name)
    length = int(m.group(1)) if m else 0
    idx = int(m.group(2)) if m else 0

    question = _build_question(example_dir, training_paths)

    record = {
        "id": example_dir.name,
        "question": question,
        # result stores the absolute target CSV path; the rollout uses it for scoring
        "result": str(target_path.resolve()),
        "extra_info": json.dumps({
            "idx": idx,
            "length": length,
            "example_dir": str(example_dir.resolve()),
            "test_csv_paths": [str(p.resolve()) for p in test_paths],
            "target_csv_path": str(target_path.resolve()),
        }),
    }
    return record


def build_dataset(
    benchmark_dir: Path,
    val_fraction: float = VAL_FRACTION,
    seed: int = RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    by_length = _discover_examples(benchmark_dir)
    print(f"Found length categories: { {k: len(v) for k, v in sorted(by_length.items())} }")

    train_dirs, val_dirs = _stratified_split(by_length, val_fraction, seed)
    print(f"Split: {len(train_dirs)} train / {len(val_dirs)} val")

    def process_batch(dirs: list[Path], label: str) -> list[dict]:
        records = []
        failed = []
        for d in dirs:
            rec = _process_example(d)
            if rec is not None:
                records.append(rec)
            else:
                failed.append(d.name)
        if failed:
            print(f"  [{label}] skipped {len(failed)} dirs (missing files): {failed[:5]}...")
        print(f"  [{label}] {len(records)} examples processed")
        return records

    train_records = process_batch(train_dirs, "train")
    val_records = process_batch(val_dirs, "val")

    train_df = pd.DataFrame(train_records)
    val_df = pd.DataFrame(val_records)
    return train_df, val_df


def main():
    parser = argparse.ArgumentParser(description="Prepare DataMorpher RL training data.")
    parser.add_argument(
        "--benchmark_dir",
        default=str(BENCHMARK_DIR),
        help="Path to autopipeline-benchmarks/github-pipelines/",
    )
    parser.add_argument(
        "--output_train",
        default=str(OUTPUT_TRAIN),
        help="Output path for train parquet",
    )
    parser.add_argument(
        "--output_val",
        default=str(OUTPUT_VAL),
        help="Output path for val parquet",
    )
    parser.add_argument(
        "--val_fraction",
        type=float,
        default=VAL_FRACTION,
        help="Fraction of each length category to hold out for validation (default 0.20)",
    )
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    train_df, val_df = build_dataset(
        Path(args.benchmark_dir),
        val_fraction=args.val_fraction,
        seed=args.seed,
    )

    for path, df, label in [
        (args.output_train, train_df, "train"),
        (args.output_val, val_df, "val"),
    ]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_parquet(path, index=False)
        print(f"Saved {label} ({len(df)} rows) → {path}")

    print("\nColumn preview:")
    print(train_df[["id", "question"]].head(2).to_string())


if __name__ == "__main__":
    main()
