"""
build_score_regression_dataset_o4mini_rerun.py
==================================================
Same as build_score_regression_dataset.py, pointed at the o4-mini rerun of
the 3 L1 new-weight regression cases (43, 81, 96) in
logs_langraph/o4mini_rerun_l1_regression/.

Usage: python3 build_score_regression_dataset_o4mini_rerun.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
sys.path.insert(0, ".")

import build_score_regression_dataset as base

base.CONFIGS = [
    (1, "logs_langraph/o4mini_rerun_l1_regression", [43, 81, 96]),
]

if __name__ == "__main__":
    sys.argv = [sys.argv[0]] + ["--output", "score_regression_dataset_o4mini_rerun.csv", "--workers", "10"] + sys.argv[1:]
    base.main()
