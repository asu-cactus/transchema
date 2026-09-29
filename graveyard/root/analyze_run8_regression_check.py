"""
analyze_run8_regression_check.py
=================================
For run8 L1 cases that were already CORRECT under the old scoring
(max(score_1, score_2) with old score_1 = (fd_f1 + avg_col_score_1)/2), check
whether the new score_1 (with row_count_score + max_missing_score added) would
pick a DIFFERENT (possibly wrong) script instead.

For each case:
  1. Extract every unique script from the log (sim + critique, all iterations).
  2. Execute each script on TRAINING data, score its output against target.csv
     with the (now-patched) value_based_relative_csv_score_timed to get the
     NEW score_1.
  3. Pick the script with the highest NEW score_1 ("new chosen").
  4. Swap training_N.csv -> test_N.csv in that script, run it, validate with
     compare_tables_matching.
  5. Report whether the new-chosen script is still correct (no regression) or
     now wrong (regression).

Usage: python3 analyze_run8_regression_check.py [case_id ...]
Run from: ~/transchema/  (needs `source env/bin/activate` first, and must be
run on mcts_utility_branch where the patched score_1 lives)
"""
import sys
import glob
import shutil
from pathlib import Path
from typing import Dict, Tuple

sys.path.insert(0, ".")
import pandas as pd

from eval_run8_training import swap_training_to_test, run_script, validate_output
from analyze_run8_failed_case_scripts import extract_all_scored_scripts
from eval_score_value_based import value_based_relative_csv_score_timed

LOG_DIR  = "logs_langraph/rag_det_score_run8_l1_training"
WORK_DIR = Path(".").resolve()

DEFAULT_CASES = [0, 3, 4, 18, 19, 21, 41, 50, 82, 89, 99]


def score_on_training(script: str, case_num: int) -> float:
    """Run script (unmodified, training paths) and score its output against
    target.csv with the current (patched) scorer. Returns new score_1, or
    0.0 on any failure."""
    ok, err = run_script(script, WORK_DIR)
    if not ok:
        return 0.0
    case_dir = WORK_DIR / f"autopipeline-benchmarks/github-pipelines/length1_{case_num}"
    out_path = case_dir / "target_multisource_mcts.csv"
    gt_path  = case_dir / "target.csv"
    if not out_path.exists() or not gt_path.exists():
        return 0.0
    try:
        df_out = pd.read_csv(out_path, low_memory=False)
        df_gt  = pd.read_csv(gt_path, low_memory=False)
        df_gt  = df_gt.drop(columns=df_gt.columns[0], axis=1)
        _, _, _, _, _, dbg = value_based_relative_csv_score_timed(df_out, df_gt, timeout=90)
        return dbg.get("score_1", 0.0) or 0.0
    except Exception:
        return 0.0


def analyze_case(case_num: int) -> Tuple[int, bool, bool]:
    """Returns (case_num, old_was_correct, new_is_correct)."""
    log_files = sorted(glob.glob(f"{LOG_DIR}/cases_c{case_num}/*.log"))
    print(f"\n{'='*90}\nCase {case_num}\n{'='*90}")
    if not log_files:
        print("  No log file found.")
        return case_num, True, None

    entries = extract_all_scored_scripts(Path(log_files[0]))
    if not entries:
        print("  No scripts extracted.")
        return case_num, True, None

    # Old chosen (Method A, highest OLD training score recorded in the log)
    old_chosen_iter, old_chosen_kind, old_chosen_script, old_chosen_score = max(
        entries, key=lambda e: e[3]
    )

    # Dedupe unique scripts, re-score each with the NEW score_1.
    seen: Dict[str, Tuple[int, str]] = {}
    for it, kind, script, _old_score in entries:
        key = script.strip()
        if key not in seen:
            seen[key] = (it, kind)

    print(f"  {len(seen)} unique scripts — rescoring each with new score_1 ...")
    rescored = []
    for script, (it, kind) in seen.items():
        new_s1 = score_on_training(script, case_num)
        rescored.append((script, it, kind, new_s1))

    n_zero = sum(1 for r in rescored if r[3] == 0.0)
    if n_zero:
        print(f"  WARNING: {n_zero}/{len(rescored)} scripts scored exactly 0.0 "
              f"(likely execution/scoring failure, not a genuine low score)")

    new_chosen = max(rescored, key=lambda r: r[3])
    same_script = new_chosen[0].strip() == old_chosen_script.strip()

    print(f"  OLD chosen: iter={old_chosen_iter} kind={old_chosen_kind} old_score={old_chosen_score:.4f}")
    print(f"  NEW chosen: iter={new_chosen[1]} kind={new_chosen[2]} new_score_1={new_chosen[3]:.4f}"
          f"  {'(SAME script as old)' if same_script else '(DIFFERENT script!)'}")

    # Validate new-chosen script on TEST data.
    test_script = swap_training_to_test(new_chosen[0])
    ok, err = run_script(test_script, WORK_DIR)
    if not ok:
        print(f"  NEW chosen script FAILED to run on test data: {err[:150]}")
        return case_num, True, False

    correct, sim = validate_output(case_num, WORK_DIR)
    print(f"  NEW chosen -> test result: {'CORRECT' if correct else 'WRONG'} (sim={sim:.3f})")

    if not correct:
        print(f"  !! REGRESSION: was correct under old scoring, now WRONG under new score_1 !!")
        print(f"  ---- NEW (regressed) chosen script ----\n{new_chosen[0]}\n  ------------------------")

    return case_num, True, correct


def main():
    cases = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else DEFAULT_CASES
    results = [analyze_case(c) for c in cases]

    print(f"\n{'='*90}\nSUMMARY\n{'='*90}")
    regressions = []
    for case_num, old_ok, new_ok in results:
        if new_ok is None:
            print(f"  case {case_num}: SKIPPED (no log/scripts)")
            continue
        status = "OK (still correct)" if new_ok else "REGRESSION (now wrong)"
        print(f"  case {case_num}: {status}")
        if not new_ok:
            regressions.append(case_num)

    print(f"\n{len(regressions)} regression(s): {regressions}")


if __name__ == "__main__":
    main()
