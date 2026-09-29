"""
Evaluate the first 10 length-1 cases using:
  1. value_based_relative_csv_score  (new score function with preprocessing)
  2. compare_tables                  (autopipeline validation)

Each length1_N folder has a flat layout:
  test_0.csv, test_1.csv, training_*.csv  — source inputs
  target.csv                              — ground truth
  python_recovered.py                     — script that reads sources and writes output
"""

import os
import re
import sys
import subprocess
import tempfile
import io
from contextlib import redirect_stdout

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from eval_score_value_based import value_based_relative_csv_score
from validation.autopipeline_match import compare_tables

BENCHMARKS_DIR = os.path.join(
    PROJECT_ROOT, "autopipeline-benchmarks", "github-pipelines"
)
N_CASES = 50


def find_length1_cases(n: int) -> list[str]:
    cases = sorted(
        [
            os.path.join(BENCHMARKS_DIR, d)
            for d in os.listdir(BENCHMARKS_DIR)
            if re.match(r"^length1_\d+$", d)
        ],
        key=lambda p: int(os.path.basename(p).split("_")[1]),
    )
    return cases[:n]


def patch_script(script_content: str, case_folder: str, output_path: str) -> str:
    """
    Rewrite all autopipeline-benchmarks relative paths in the script:
      - test_N.csv / training_N.csv  → absolute path inside case_folder
      - any other .csv (output file) → output_path
    """
    pattern = re.compile(
        r'([\'"])([^\'"]*autopipeline-benchmarks/github-pipelines/[^/]+/([^\'"]+))\1'
    )

    def replace_path(m):
        quote = m.group(1)
        filename = m.group(3)
        if filename.startswith("test_") or filename.startswith("training_"):
            return f"{quote}{os.path.join(case_folder, filename)}{quote}"
        else:
            return f"{quote}{output_path}{quote}"

    return pattern.sub(replace_path, script_content)


def run_script(case_folder: str) -> tuple[pd.DataFrame | None, str | None]:
    script_path = os.path.join(case_folder, "python_recovered.py")
    output_csv = os.path.join(case_folder, "_eval_output.csv")

    with open(script_path) as f:
        original = f.read()

    patched = patch_script(original, case_folder, output_csv)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(tmp_fd, "w") as sf:
            sf.write(patched)
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
    finally:
        os.unlink(tmp_path)

    if result.returncode != 0:
        return None, result.stderr.strip()

    if not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0:
        return None, "Script ran but produced no output CSV."

    try:
        df = pd.read_csv(output_csv)
    except Exception as e:
        return None, f"Could not read output CSV: {e}"
    finally:
        if os.path.exists(output_csv):
            os.unlink(output_csv)

    return df, None


def drop_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[c for c in df.columns if c.startswith("Unnamed:")], errors="ignore")


def evaluate_case(case_folder: str) -> dict:
    case_name = os.path.basename(case_folder)
    target_path = os.path.join(case_folder, "target.csv")

    if not os.path.exists(target_path):
        return {"case": case_name, "success": False, "error": "target.csv not found"}

    try:
        df_gt = drop_unnamed(pd.read_csv(target_path))
    except Exception as e:
        return {"case": case_name, "success": False, "error": f"Could not read target.csv: {e}"}

    df_pred, error = run_script(case_folder)
    if df_pred is None:
        return {"case": case_name, "success": False, "error": error}

    df_pred = drop_unnamed(df_pred)

    # --- Value-based score (new score function) ---
    try:
        fd_ratio, col_ratio, combined, fd_f1, true_combined, debug = \
            value_based_relative_csv_score(df_pred, df_gt)
    except Exception as e:
        fd_ratio = col_ratio = combined = fd_f1 = true_combined = None
        debug = {"error": str(e)}

    # --- Autopipeline validation ---
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            ap_match, ap_matched_cols = compare_tables(df_pred.copy(), df_gt.copy())
    except Exception as e:
        ap_match = False
        ap_matched_cols = []

    return {
        "case": case_name,
        "success": True,
        "error": None,
        # value-based score
        "fd_f1":             fd_f1,
        "true_combined":     true_combined,
        "fd_ratio":          fd_ratio,
        "col_ratio":         col_ratio,
        "combined":          combined,
        "column_map":        debug.get("jaccard_column_map", []),
        "avg_column_score":  debug.get("column_scores", {}).get("avg_column_score"),
        # autopipeline validation
        "ap_match":          ap_match,
        "ap_matched_cols":   ap_matched_cols,
    }


def main():
    cases = find_length1_cases(N_CASES)
    print(f"Evaluating {len(cases)} length-1 cases\n")

    results = []
    for case_folder in cases:
        case_name = os.path.basename(case_folder)
        print(f"{'='*60}")
        print(f"Case: {case_name}")
        print("=" * 60)

        r = evaluate_case(case_folder)
        results.append(r)

        if not r["success"]:
            print(f"  ERROR: {r['error']}")
            continue

        print(f"  [Value-Based Score]")
        print(f"    fd_f1            : {r['fd_f1']}")
        print(f"    avg_column_score : {r['avg_column_score']}")
        print(f"    true_combined    : {r['true_combined']}")

        if r["column_map"]:
            print(f"  [Column Mapping]")
            for m in r["column_map"]:
                print(f"    GT: {m['gt_col']:<30} <- GEN: {m['gen_col']:<30} ({m['jaccard']:.4f})")

        print(f"  [Autopipeline Validation]")
        print(f"    match            : {r['ap_match']}")
        print(f"    matched_cols     : {r['ap_matched_cols']}")
        print()

    # --- Summary ---
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    ap_passed = [r for r in successful if r["ap_match"]]

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total cases        : {len(results)}")
    print(f"  Successful runs    : {len(successful)}")
    print(f"  Autopipeline pass  : {len(ap_passed)}")
    print(f"  Errors             : {len(failed)}")

    if successful:
        mean_tc = sum(r["true_combined"] for r in successful if r["true_combined"] is not None) / len(successful)
        print(f"  Mean true_combined : {mean_tc:.4f}")

    if ap_passed:
        print("\nAutopipeline passed cases:")
        for r in ap_passed:
            print(f"  [PASS] {r['case']}")

    # --- Disagreement analysis ---
    ap_true_score_low  = [r for r in successful if r["ap_match"] and (r["true_combined"] or 0.0) < 1.0]
    score_full_ap_false = [r for r in successful if not r["ap_match"] and (r["true_combined"] or 0.0) >= 1.0]

    if ap_true_score_low:
        print(f"\nDisagreement — Autopipeline=True but score < 1.0 ({len(ap_true_score_low)} cases):")
        for r in ap_true_score_low:
            print(f"  {r['case']}: true_combined={r['true_combined']}")

    if score_full_ap_false:
        print(f"\nDisagreement — score=1.0 but Autopipeline=False ({len(score_full_ap_false)} cases):")
        for r in score_full_ap_false:
            print(f"  {r['case']}: true_combined={r['true_combined']}")

    if failed:
        print("\nFailed cases:")
        for r in failed:
            print(f"  [FAIL] {r['case']}: {(r['error'] or '')[:120]}")


if __name__ == "__main__":
    main()
