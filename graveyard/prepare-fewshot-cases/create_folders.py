#!/usr/bin/env python3
"""
Make experiment subfolders:

Given: a list of numbers n1, n2, n3, ..., a base folder `my_dir`, and a number L
Create subfolders:
  my_dir/Length{L}_n1, my_dir/Length{L}_n2, ...
Each subfolder contains:
  - Prompts(The last one includes successful answer)
  - Source_datasets
  - Target_datasets
"""

from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Iterable

PROMPTS_DIR_NAME = "Prompts(The last one includes successful answer)"
SOURCE_DIR_NAME = "Source_datasets"
TARGET_DIR_NAME = "Target_datasets"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create structured subfolders for a set of numbers.")
    p.add_argument(
        "--dir", "-d", required=True,
        help="Base directory (e.g., ./my_dir). Will be created if it doesn't exist."
    )
    p.add_argument(
        "--length", "-L", required=True, type=str,
        help="Length value L to use in folder names (kept as string)."
    )
    p.add_argument(
        "numbers", nargs="+",
        help="List of numbers (e.g., 10 25 100). They are used verbatim in folder names."
    )
    return p.parse_args()

def ensure_dirs(base: Path, L: str, ns: Iterable[str]) -> List[Path]:
    created: List[Path] = []
    base.mkdir(parents=True, exist_ok=True)

    for n in ns:
        subdir = base / f"Length{L}_{n}"
        # Create the subdir and the three required children
        (subdir / PROMPTS_DIR_NAME).mkdir(parents=True, exist_ok=True)
        (subdir / SOURCE_DIR_NAME).mkdir(parents=True, exist_ok=True)
        (subdir / TARGET_DIR_NAME).mkdir(parents=True, exist_ok=True)
        created.append(subdir)

    return created

def main():
    args = parse_args()
    base = Path(args.dir)
    L = str(args.length)
    numbers = [str(x) for x in args.numbers]

    created = ensure_dirs(base, L, numbers)

    print(f"Base directory: {base.resolve()}")
    print(f"Created/verified {len(created)} subfolders:")
    for p in created:
        print(f"  {p}")
        print(f"    - {PROMPTS_DIR_NAME}")
        print(f"    - {SOURCE_DIR_NAME}")
        print(f"    - {TARGET_DIR_NAME}")

if __name__ == "__main__":
    main()

