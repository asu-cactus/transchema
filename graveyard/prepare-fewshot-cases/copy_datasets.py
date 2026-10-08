#!/usr/bin/env python3
"""
Copy experiment artifacts from src_dir to dest_dir for a given L and list of N's.

For each N in [N1, N2, ...], this script copies:
  - {src_dir}/length{L}_{N}/test*.csv     -> {dest_dir}/Length{L}_{N}/Source_datasets/
  - {src_dir}/length{L}_{N}/target.csv    -> {dest_dir}/Length{L}_{N}/Target_datasets/
  - {src_dir}/length{L}_{N}/python_recovered.py (if exists)
                                          -> {dest_dir}/Length{L}_{N}/

Notes
-----
- Destination folders are created as needed.
- Existing files are overwritten (copy2 preserves timestamps).
- Missing files are reported but do not abort the run.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys
from glob import glob

SRC_SUB_FMT = "length{L}_{N}"
DST_SUB_FMT = "Length{L}_{N}"

SRC_TEST_GLOB = "test*.csv"
SRC_TARGET_NAME = "target.csv"
SRC_RECOVERED = "python_recovered.py"

SRC_DIRS = ("Source_datasets", "Target_datasets")  # only for naming in prints

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Copy test/target/recovered files into structured dest folders.")
    p.add_argument("--src-dir", "-s", required=True, help="Source directory containing length{L}_{N}/ subfolders")
    p.add_argument("--dest-dir", "-d", required=True, help="Destination base directory to receive files")
    p.add_argument("--length", "-L", required=True, help="Length value L (used as string in paths)")
    p.add_argument("numbers", nargs="+", help="List of N values (e.g., 10 25 100)")
    return p.parse_args()

def ensure_dirs(dest_base: Path, L: str, N: str) -> dict[str, Path]:
    """Create destination structure and return paths."""
    dst_root = dest_base / DST_SUB_FMT.format(L=L, N=N)
    dst_src = dst_root / "Source_datasets"
    dst_tgt = dst_root / "Target_datasets"

    dst_src.mkdir(parents=True, exist_ok=True)
    dst_tgt.mkdir(parents=True, exist_ok=True)
    dst_root.mkdir(parents=True, exist_ok=True)  # safe even if exists

    return {"root": dst_root, "src": dst_src, "tgt": dst_tgt}

def copy_for_N(src_base: Path, dest_base: Path, L: str, N: str) -> dict[str, int]:
    """Copy files for one N; return counts of copied files."""
    src_sub = src_base / SRC_SUB_FMT.format(L=L, N=N)
    dst_paths = ensure_dirs(dest_base, L, N)

    counts = {"source_csv": 0, "target_csv": 0, "recovered_py": 0, "missing": 0}

    if not src_sub.exists():
        print(f"[WARN] Missing source folder: {src_sub}", file=sys.stderr)
        counts["missing"] += 1
        return counts

    # 1) test*.csv -> Source_datasets
    test_glob = str(src_sub / SRC_TEST_GLOB)
    for fpath in sorted(glob(test_glob)):
        src = Path(fpath)
        if src.is_file():
            shutil.copy2(src, dst_paths["src"] / src.name)
            counts["source_csv"] += 1

    if counts["source_csv"] == 0:
        print(f"[INFO] No test*.csv found for N={N} in {src_sub}", file=sys.stderr)

    # 2) target.csv -> Target_datasets
    target_src = src_sub / SRC_TARGET_NAME
    if target_src.exists() and target_src.is_file():
        shutil.copy2(target_src, dst_paths["tgt"] / target_src.name)
        counts["target_csv"] += 1
    else:
        print(f"[INFO] Missing target.csv for N={N} in {src_sub}", file=sys.stderr)

    # 3) python_recovered.py (optional) -> root of Length{L}_{N}
    recovered_src = src_sub / SRC_RECOVERED
    if recovered_src.exists() and recovered_src.is_file():
        shutil.copy2(recovered_src, dst_paths["root"] / recovered_src.name)
        counts["recovered_py"] += 1

    return counts

def main():
    args = parse_args()
    src_base = Path(args.src_dir)
    dest_base = Path(args.dest_dir)
    L = str(args.length)
    numbers = [str(n) for n in args.numbers]

    total = {"source_csv": 0, "target_csv": 0, "recovered_py": 0, "missing": 0}

    for N in numbers:
        counts = copy_for_N(src_base, dest_base, L, N)
        total = {k: total.get(k, 0) + counts.get(k, 0) for k in set(total) | set(counts)}
        print(
            f"N={N}: copied {counts['source_csv']} test*.csv, "
            f"{counts['target_csv']} target.csv, "
            f"{counts['recovered_py']} python_recovered.py"
        )

    print(
        f"Done. Totals -> test*.csv: {total['source_csv']}, "
        f"target.csv: {total['target_csv']}, "
        f"python_recovered.py: {total['recovered_py']}, "
        f"missing source folders: {total['missing']}"
    )

if __name__ == "__main__":
    main()

