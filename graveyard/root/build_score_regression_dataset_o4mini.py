"""
build_score_regression_dataset_o4mini.py
===========================================
Same as build_score_regression_dataset.py, but pointed at the o4-mini +
early-stopping HYBRID-failed retry experiment (run_o4mini_earlystop_hybrid_failed.sh)
instead of run9-training. Needed to compute NEW-weight scores for this
experiment, since score_regression_dataset.csv only covers run9-training
L1/L4/L9 -- it has no coverage for these logs at all.

Usage:
  python3 build_score_regression_dataset_o4mini.py [--workers 30]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
sys.path.insert(0, ".")

import build_score_regression_dataset as base

L1_CASES = [8, 22, 24, 44, 54, 64, 75, 85, 86, 89, 90, 91, 93, 95, 97, 99]
L4_CASES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
            22, 23, 24, 28, 29, 30, 35, 36, 37, 40, 43, 45, 46, 47, 48, 49, 50, 51, 52,
            53, 58, 60, 61, 62, 63, 64, 68, 70, 71, 73, 84, 86, 87, 92, 93, 94, 96, 97,
            98, 99]
L9_CASES = [1, 3, 4, 13, 15, 16, 19, 20, 21, 22, 23, 24, 27, 29, 35, 36, 38, 40, 41, 42,
            43, 44, 45, 46, 62, 67, 68, 69, 70, 71, 72, 73, 74]

base.CONFIGS = [
    (1, "logs_langraph/o4mini_earlystop_hybrid_failed_l1", L1_CASES),
    (4, "logs_langraph/o4mini_earlystop_hybrid_failed_l4", L4_CASES),
    (9, "logs_langraph/o4mini_earlystop_hybrid_failed_l9", L9_CASES),
]

if __name__ == "__main__":
    sys.argv = [sys.argv[0]] + ["--output", "score_regression_dataset_o4mini.csv"] + sys.argv[1:]
    base.main()
