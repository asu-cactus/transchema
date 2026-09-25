"""
Debug timing of GT FD cache and det_score for L4 wide-column cases 4_30 and 4_37.
Tests with no truncation (full table) and truncation at 15 and 20 cols.
Usage: python3 debug_timing_l4.py
Run from: ~/transchema/
"""
import time, os, sys
import pandas as pd
sys.path.insert(0, ".")
sys.path.insert(0, "eval_score")

BASE = "autopipeline-benchmarks/github-pipelines"

import fdtool.fdtool as _fdtool
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FTE
from eval_score_value_based import value_based_relative_csv_score_timed
from validation.fuzzy_match import compare_tables_fuzzy

def run_fd(df, timeout=120):
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(_fdtool.main, df)
        try:
            r = fut.result(timeout=timeout)
            return r, False
        except FTE:
            return ([], [], []), True

for length, case_id in [(4, 30), (4, 37)]:
    print(f"\n{'='*60}")
    print(f"  {length}_{case_id}")
    print(f"{'='*60}")

    gt_path   = f"{BASE}/length{length}_{case_id}/target.csv"
    src_files = sorted(f for f in os.listdir(f"{BASE}/length{length}_{case_id}") if f.startswith("training_"))
    print(f"  GT: {os.path.getsize(gt_path)//1024}KB")
    for sf in src_files:
        print(f"  {sf}: {os.path.getsize(f'{BASE}/length{length}_{case_id}/{sf}')//1024}KB")

    t0 = time.perf_counter()
    df_gt = pd.read_csv(gt_path, low_memory=False)
    df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
    print(f"\n  [1] Load GT {df_gt.shape}: {time.perf_counter()-t0:.2f}s")

    # ── No truncation (full table) ─────────────────────────────────────────────
    print(f"\n  --- No truncation ({df_gt.shape[0]}r × {df_gt.shape[1]}c) ---")

    t0 = time.perf_counter()
    _, timed_out = run_fd(df_gt.iloc[:, :52], timeout=60)
    print(f"  [2] GT FD mining (full): {time.perf_counter()-t0:.2f}s  {'TIMED OUT' if timed_out else 'OK'}")

    t0 = time.perf_counter()
    try:
        res = value_based_relative_csv_score_timed(df_gt.copy(), df_gt, timeout=60)
        print(f"  [3] det_score (full):    {time.perf_counter()-t0:.2f}s  score={res[4]:.4f}")
    except Exception as e:
        print(f"  [3] det_score (full):    {time.perf_counter()-t0:.2f}s  TIMEOUT/ERROR: {e}")

    # ── Truncation at 15 and 20 cols ──────────────────────────────────────────
    for n_cols in [15, 20]:
        n_rows = 2000
        df_trunc = df_gt.iloc[:n_rows, :n_cols]
        print(f"\n  --- First {n_cols} cols × {n_rows} rows ---")

        t0 = time.perf_counter()
        _, timed_out = run_fd(df_trunc, timeout=60)
        print(f"  [2] GT FD mining ({n_cols}c): {time.perf_counter()-t0:.2f}s  {'TIMED OUT' if timed_out else 'OK'}")

        t0 = time.perf_counter()
        try:
            res = value_based_relative_csv_score_timed(df_trunc.copy(), df_trunc, timeout=60)
            print(f"  [3] det_score ({n_cols}c):    {time.perf_counter()-t0:.2f}s  score={res[4]:.4f}")
        except Exception as e:
            print(f"  [3] det_score ({n_cols}c):    {time.perf_counter()-t0:.2f}s  TIMEOUT/ERROR: {e}")

    # ── Partial reward baseline ────────────────────────────────────────────────
    t0 = time.perf_counter()
    partial, _ = compare_tables_fuzzy(df_gt.copy(), df_gt)
    print(f"\n  [4] partial reward (full): {time.perf_counter()-t0:.2f}s  score={partial:.4f}")
