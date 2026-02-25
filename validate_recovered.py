"""
Validate all python_recovered.py files against their ground truth target CSVs
using compare_lists_matching from validation/hard_match.py.

Each case folder structure:
  <base_dir>/Length4_XX/
      python_recovered.py       # script that reads Source_datasets/* and writes output
      Source_datasets/test_N.csv
      Target_datasets/target.csv   # ground truth

The scripts hardcode paths like:
  'autopipeline-benchmarks/github-pipelines/length4_XX/test_N.csv'
This script patches those to absolute paths before execution.
"""

import os
import re
import sys
import subprocess
import tempfile

import pandas as pd

# Ensure project root is on path for validation imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from validation.hard_match import compare_lists_matching


def find_case_folders(base_dir: str) -> list[str]:
    """Return sorted list of folders that contain python_recovered.py."""
    cases = []
    for entry in sorted(os.scandir(base_dir), key=lambda e: e.name):
        if entry.is_dir():
            script = os.path.join(entry.path, "python_recovered.py")
            if os.path.exists(script):
                cases.append(entry.path)
    return cases


def patch_script(script_content: str, source_dir: str, output_path: str) -> str:
    """
    Replace relative autopipeline paths in the script with absolute paths.

    Replaces:
      - Any quoted path matching  autopipeline-benchmarks/github-pipelines/<folder>/test_N.csv
        -> absolute path inside source_dir
      - Any quoted path matching  autopipeline-benchmarks/github-pipelines/<folder>/<name>.csv
        -> output_path (the temp output file)
    """
    # Pattern: quoted string that contains the autopipeline prefix
    # Group 1 = quote char, Group 2 = full path inside quotes
    pattern = re.compile(
        r'([\'"])([^\'\"]*autopipeline-benchmarks/github-pipelines/[^/]+/([^\'"]+))\1'
    )

    def replace_path(m):
        quote = m.group(1)
        filename = m.group(3)  # e.g. test_0.csv or target_multisource_cot.csv
        if filename.startswith("test_"):
            return f"{quote}{os.path.join(source_dir, filename)}{quote}"
        else:
            # output file
            return f"{quote}{output_path}{quote}"

    return pattern.sub(replace_path, script_content)


def run_patched_script(case_folder: str) -> tuple[pd.DataFrame | None, str | None]:
    """
    Patch and execute python_recovered.py for the given case folder.
    Output CSV is saved to <case_folder>/Target_datasets/python_recovered_output.csv
    so it can be inspected alongside target.csv.
    Returns (output_dataframe, error_message).
    """
    script_path = os.path.join(case_folder, "python_recovered.py")
    source_dir = os.path.join(case_folder, "Source_datasets")
    output_csv = os.path.join(case_folder, "Target_datasets", "python_recovered_output.csv")

    with open(script_path, "r") as f:
        original = f.read()

    patched = patch_script(original, source_dir, output_csv)

    # Write patched script to a temp file and run it as a subprocess
    tmp_sfd, tmp_script = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(tmp_sfd, "w") as sf:
            sf.write(patched)
        result = subprocess.run(
            [sys.executable, tmp_script],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
    finally:
        os.unlink(tmp_script)

    if result.returncode != 0:
        return None, result.stderr.strip()

    if not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0:
        return None, "Script ran but produced no output CSV."

    try:
        df = pd.read_csv(output_csv)
    except Exception as e:
        return None, f"Failed to read output CSV: {e}"

    return df, None


def validate_case(case_folder: str) -> dict:
    case_name = os.path.basename(case_folder)
    target_path = os.path.join(case_folder, "Target_datasets", "target.csv")

    if not os.path.exists(target_path):
        return {"case": case_name, "success": False, "error": "target.csv not found"}

    try:
        ground_truth_df = pd.read_csv(target_path)
    except Exception as e:
        return {
            "case": case_name,
            "success": False,
            "error": f"Could not read target.csv: {e}",
        }

    pred_df, error = run_patched_script(case_folder)
    if pred_df is None:
        return {"case": case_name, "success": False, "error": error}

    try:
        avg_sim, exact_match, similarities, matched_cols = compare_lists_matching(
            pred_df, ground_truth_df
        )
    except Exception as e:
        return {
            "case": case_name,
            "success": False,
            "error": f"compare_lists_matching failed: {e}",
        }

    return {
        "case": case_name,
        "success": True,
        "avg_similarity": avg_sim,
        "exact_match": exact_match,
        "similarities": similarities,
        "matched_columns": matched_cols,
        "error": None,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate python_recovered.py files against ground truth."
    )
    parser.add_argument(
        "base_dir",
        nargs="?",
        default=os.path.join(PROJECT_ROOT, "examples_length_4", "examples_length_4"),
        help="Base directory containing Length4_XX case folders.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-column output from hard_match.",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.base_dir):
        print(f"ERROR: Directory not found: {args.base_dir}")
        sys.exit(1)

    cases = find_case_folders(args.base_dir)
    if not cases:
        print("No cases with python_recovered.py found.")
        sys.exit(0)

    print(f"Found {len(cases)} case(s) in: {args.base_dir}\n")

    results = []
    for case_folder in cases:
        case_name = os.path.basename(case_folder)
        print(f"{'='*60}")
        print(f"Validating: {case_name}")
        print("=" * 60)

        if args.quiet:
            # Suppress stdout from compare_lists_matching
            import io
            from contextlib import redirect_stdout

            buf = io.StringIO()
            with redirect_stdout(buf):
                result = validate_case(case_folder)
        else:
            result = validate_case(case_folder)

        results.append(result)

        if result["success"]:
            print(f"  Avg Similarity : {result['avg_similarity']:.4f}")
            print(f"  Exact Match    : {result['exact_match']}")
            print(f"  Matched cols   : {result['matched_columns']}")
        else:
            print(f"  ERROR: {result['error']}")
        print()

    # --- Summary ---
    successful = [r for r in results if r["success"]]
    exact = [r for r in successful if r["exact_match"]]
    failed = [r for r in results if not r["success"]]

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total cases      : {len(results)}")
    print(f"  Successful runs  : {len(successful)}")
    print(f"  Exact matches    : {len(exact)}")
    print(f"  Errors           : {len(failed)}")
    if successful:
        avg = sum(r["avg_similarity"] for r in successful) / len(successful)
        print(f"  Mean similarity  : {avg:.4f}")

    if exact:
        print("\nExact match cases:")
        for r in exact:
            print(f"  [PASS] {r['case']}")

    if failed:
        print("\nFailed / errored cases:")
        for r in failed:
            print(f"  [FAIL] {r['case']}: {(r['error'] or '')[:120]}")

    # Return exit code 0 only if all cases pass
    sys.exit(0 if len(exact) == len(results) else 1)


if __name__ == "__main__":
    main()
