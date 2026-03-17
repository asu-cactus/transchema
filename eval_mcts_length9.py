"""
Evaluate target_multisource_mcts.csv against target.csv for cases length9_65 through length9_70.

Reports:
  - relative_csv_score metrics (fd_ratio, col_ratio, fd_f1, true_combined_score)
  - autopipeline validation result (compare_tables pass/fail)
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from eval_score.score import relative_csv_score
from validation.autopipeline_match import compare_tables

BENCHMARKS_DIR = os.path.join(
    os.path.dirname(__file__),
    "autopipeline-benchmarks", "github-pipelines"
)

CASES = [f"length9_{i}" for i in range(65, 80)]  # 9_65 to 9_70

header = f"{'Case':<15} {'fd_ratio':>9} {'col_ratio':>9} {'fd_f1':>9} {'true_comb':>10} {'valid':>7}"
print(header)
print("-" * len(header))

for case in CASES:
    target_path = os.path.join(BENCHMARKS_DIR, case, "target.csv")
    mcts_path   = os.path.join(BENCHMARKS_DIR, case, "target_multisource_mcts.csv")

    if not os.path.exists(target_path):
        print(f"{case:<15} {'MISSING target.csv':>50}")
        continue
    if not os.path.exists(mcts_path):
        print(f"{case:<15} {'MISSING target_multisource_mcts.csv':>50}")
        continue

    df_target = pd.read_csv(target_path, low_memory=False)
    if df_target.columns[0].startswith("Unnamed"):
        df_target = df_target.drop(columns=df_target.columns[0])

    df_mcts = pd.read_csv(mcts_path, low_memory=False)
    if df_mcts.columns[0].startswith("Unnamed"):
        df_mcts = df_mcts.drop(columns=df_mcts.columns[0])

    # --- Relative score (mcts vs target) ---
    try:
        fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, _ = relative_csv_score(
            df_mcts.iloc[:1000, :15],
            df_target.iloc[:1000, :15],
        )
        score_str = (
            f" {fd_ratio:>9.4f}"
            f" {col_ratio:>9.4f}"
            f" {fd_f1:>9.4f}"
            f" {true_combined_score:>10.4f}"
        )
    except Exception as e:
        score_str = f" {'ERROR: ' + str(e)[:40]:>39}"

    # --- Autopipeline validation ---
    try:
        is_correct, _ = compare_tables(df_mcts, df_target)
        valid_str = f"{'PASS' if is_correct else 'FAIL':>7}"
    except Exception as e:
        valid_str = f"{'ERR':>7}"

    print(f"{case:<15}{score_str} {valid_str}")
