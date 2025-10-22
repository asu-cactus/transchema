#!/usr/bin/env python3
"""
Rename folders one level down:
Within each first-level subfolder of BASE_DIR, if there is a subfolder named
'Prompts(The last one includes successful answer)', rename it to 'Prompts'.

- Scope: BASE_DIR/*/*/
- If 'Prompts' already exists under the same parent, contents are merged.
- Prints a summary.

Usage:
  python rename_prompts_level2.py /path/to/base_dir
"""

from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

OLD_NAME = "Prompts(The last one includes successful answer)"
NEW_NAME = "Prompts"

def merge_dirs(src: Path, dst: Path) -> None:
    """Move contents of src into dst, creating dst if needed."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if target.exists():
            if item.is_dir() and target.is_dir():
                merge_dirs(item, target)
                try:
                    item.rmdir()
                except OSError:
                    pass
            else:
                # Resolve conflicts: replace target with src
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                shutil.move(str(item), str(target))
        else:
            shutil.move(str(item), str(target))

def main():
    ap = argparse.ArgumentParser(
        description="Rename 'Prompts(The last one includes successful answer)' to 'Prompts' one level down."
    )
    ap.add_argument("base_dir", help="Base directory whose immediate subfolders will be scanned.")
    args = ap.parse_args()

    base = Path(args.base_dir)
    if not base.exists() or not base.is_dir():
        print(f"ERROR: {base} does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    checked_parents = 0
    renamed = 0
    merged = 0
    skipped = 0

    # Iterate first-level subfolders
    for parent in base.iterdir():
        if not parent.is_dir():
            continue
        checked_parents += 1
        # Iterate *immediate* subfolders of this parent
        for sub in parent.iterdir():
            if not sub.is_dir():
                continue
            if sub.name == OLD_NAME:
                old_path = sub
                new_path = parent / NEW_NAME
                if new_path.exists() and new_path.is_dir():
                    merge_dirs(old_path, new_path)
                    # Try to remove old (now empty) dir; fall back to rmtree
                    try:
                        old_path.rmdir()
                    except OSError:
                        shutil.rmtree(old_path, ignore_errors=True)
                    merged += 1
                    print(f"[MERGED] {old_path} -> {new_path}")
                else:
                    old_path.rename(new_path)
                    renamed += 1
                    print(f"[RENAMED] {old_path} -> {new_path}")
            else:
                skipped += 1

    print("\nSummary:")
    print(f"  First-level parents scanned: {checked_parents}")
    print(f"  Renamed: {renamed}")
    print(f"  Merged into existing 'Prompts': {merged}")
    print(f"  Other subfolders seen (skipped): {skipped}")

if __name__ == "__main__":
    main()

