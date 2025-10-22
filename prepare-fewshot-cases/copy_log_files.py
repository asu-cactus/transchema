#!/usr/bin/env python3
"""
Copy logs by prefix into experiment Prompt folders.

Given:
  - log_dir: base folder that contains a subfolder 'logs/'
  - my_dir: destination base folder
  - L: the length value used in file prefixes and destination folder names
  - N1, N2, N3, ...

For each N:
  - Find all files directly under {log_dir}/logs/ whose filename starts with "{L}_target{N}"
  - Copy them to:
      {my_dir}/Length{L}_{N}/Prompts/

Notes:
  - Destination folders are created if missing.
  - Only files directly inside {log_dir}/logs/ are considered (no recursion).
  - Existing files are overwritten to ensure the latest copy.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

PROMPTS_DIR_NAME = "Prompts"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Copy prefixed log files into per-N Prompt folders.")
    p.add_argument("--log-dir", "-g", required=True, help="Folder containing 'logs/' (e.g., ./log_dir)")
    p.add_argument("--dest", "--my-dir", "-d", required=True, help="Destination base directory (my_dir)")
    p.add_argument("--length", "-L", required=True, help="Length value L used in names/prefixes (kept as string)")
    p.add_argument("numbers", nargs="+", help="List of N values (e.g., 10 25 100)")
    return p.parse_args()

def copy_for_number(logs_dir: Path, dest_base: Path, L: str, N: str) -> int:
    """Copy files with prefix '{L}_target{N}_' from logs_dir to the target Prompts folder."""
    prefix = f"{L}_target{N}_"
    # Build destination
    dest_prompts = dest_base / f"Length{L}_{N}" / PROMPTS_DIR_NAME
    dest_prompts.mkdir(parents=True, exist_ok=True)

    copied = 0
    # Iterate only files directly under logs_dir
    for entry in logs_dir.iterdir():
        if entry.is_file() and entry.name.startswith(prefix):
            shutil.copy2(entry, dest_prompts / entry.name)
            copied += 1
    return copied

def main():
    args = parse_args()
    log_dir = Path(args.log_dir)
    logs_dir = log_dir / "logs"
    if not logs_dir.exists() or not logs_dir.is_dir():
        print(f"ERROR: '{logs_dir}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    dest_base = Path(args.dest)
    L = str(args.length)
    numbers = [str(n) for n in args.numbers]

    total = 0
    for n in numbers:
        count = copy_for_number(logs_dir, dest_base, L, n)
        total += count
        print(f"N={n}: copied {count} file(s) to {dest_base / f'Length{L}_{n}' / PROMPTS_DIR_NAME}")

    print(f"Done. Total files copied: {total}")

if __name__ == "__main__":
    main()

