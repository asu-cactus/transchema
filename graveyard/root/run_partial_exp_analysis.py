"""
MCTS experiment analysis pipeline — script-granularity output.
Supports two experiment modes:
  --experiment partial  → rag_global_partial_pipeline  (L1/L5, reward=partial, test split)
  --experiment score    → rag_det_score_l149           (L1/L4/L9, reward=det_score_value, test split)

Output CSV has one row per script per case, with:
  - partial score and det_score on both TEST and TRAINING data
  - det_score broken down into numeric and categorical column averages
  - det timing: preprocess_ms (column alignment), fd_ms (FD mining), col_ms

Usage:
    source env/bin/activate
    python3 run_partial_exp_analysis.py --experiment score --lengths 1 4 9 --workers 8
    python3 run_partial_exp_analysis.py --experiment partial --lengths 1 5 --workers 8
Run from: ~/transchema/
"""

import argparse, csv, glob, os, re, subprocess, sys, tempfile, time
from multiprocessing import Pool
sys.path.insert(0, ".")

import numpy as np
import pandas as pd

from validation.fuzzy_match import compare_tables_fuzzy
import eval_score_value_based as vb
from eval_score.score import relative_csv_score

# ── Config ────────────────────────────────────────────────────────────────────
DATA_BASE    = "autopipeline-benchmarks/github-pipelines"
LOG_BASE     = "logs_langraph"
RESULTS_BASE = "Langraph/results_langraph"


def get_experiment_config(experiment: str):
    """
    Return (log_dirs_by_length, result_dirs_by_length, base_split) for the chosen experiment.

    partial        → rag_global_partial_pipeline  (L1/L5, reward=partial,         test split)
    score          → rag_det_score_l149           (L1/L4/L9, reward=det_score,    test split)
    score_t1_train → rag_det_score_t1_train       (L1/L4/L9, reward=det_score,    training split)
                     19 cases that timed out; scripts reference training_N.csv.
    """
    if experiment == "partial":
        log_dirs = {
            1: sorted(glob.glob(f"{LOG_BASE}/mcts_l1_p*_rag_global_partial_pipeline")),
            5: sorted(glob.glob(f"{LOG_BASE}/mcts_l5_p*_rag_global_partial_pipeline")),
        }
        res_dirs = {
            1: sorted(glob.glob(f"{RESULTS_BASE}/mcts_l1_p*_rag_global_partial_pipeline_*/")),
            5: sorted(glob.glob(f"{RESULTS_BASE}/mcts_l5_p*_rag_global_partial_pipeline_*/")),
        }
        return log_dirs, res_dirs, "test"

    elif experiment == "score":
        log_dirs, res_dirs = {}, {}
        for L in [1, 4, 9]:
            log_dirs[L] = (
                sorted(glob.glob(f"{LOG_BASE}/rag_det_score_l149/cases_l{L}_p*")) +
                sorted(glob.glob(f"{LOG_BASE}/rag_det_score_l149/cases_rerun*_{L}_*"))
            )
            res_dirs[L] = (
                sorted(glob.glob(f"{RESULTS_BASE}/rag_det_score_l149/rag_det_score_l{L}_p*/")) +
                sorted(glob.glob(f"{RESULTS_BASE}/rag_det_score_l149/rag_det_score_rerun*_{L}_*/"))
            )
        return log_dirs, res_dirs, "test"

    elif experiment == "score_t1_train":
        # Scripts reference training_N.csv (MCTS ran on training data).
        # Each case has its own log subdir: cases_t1_train_{case_id}/
        # Results: rag_det_score_t1_train/rag_det_t1_train_{case_id}_{ts}/
        log_dirs, res_dirs = {}, {}
        for L in [1, 4, 9]:
            log_dirs[L] = sorted(glob.glob(
                f"{LOG_BASE}/rag_det_score_t1_train/cases_t1_train_{L}_*"
            ))
            res_dirs[L] = sorted(glob.glob(
                f"{RESULTS_BASE}/rag_det_score_t1_train/rag_det_t1_train_{L}_*/"
            ))
        return log_dirs, res_dirs, "training"

    else:
        raise ValueError(f"Unknown experiment: {experiment!r}. "
                         f"Choose 'partial', 'score', or 'score_t1_train'.")



# ── Helpers: script extraction ────────────────────────────────────────────────

def extract_scripts_from_log(log_path):
    """Return list of (script_idx, logged_test_partial, code)."""
    lines = open(log_path).readlines()
    results = []
    in_s, buf = False, []
    for i, line in enumerate(lines):
        if re.match(r"^```[Pp]ython\s*$", line.strip()):
            buf = []; in_s = True; continue
        if in_s:
            if line.strip() == "```":
                code = "".join(buf).strip()
                if code and not code.startswith("<"):
                    score = None
                    for j in range(i + 1, min(i + 25, len(lines))):
                        m = re.search(r"execute_and_score.*reward=([\d.]+)", lines[j])
                        if m: score = float(m.group(1)); break
                    results.append((len(results) + 1, score, code))
                in_s = False; buf = []
            else:
                buf.append(line)
    return results  # [(idx, logged_partial, code), ...]


def find_log(length, case_num, log_dirs):
    """Find the most-recent MCTS log file for a given (length, case_num)."""
    best = None
    for d in log_dirs:
        pattern = f"{d}/{length}_target{case_num}_MCTS_*.log"
        for f in glob.glob(pattern):
            ts = re.search(r"MCTS_(\d+_\d+)\.log", f)
            ts = ts.group(1) if ts else ""
            if best is None or ts > best[1]:
                best = (f, ts)
    return best[0] if best else None


# ── Helpers: timed scoring ────────────────────────────────────────────────────

def _timed_det_score(df_gen, df_gt):
    """
    Returns (true_combined_score, preprocess_ms, fd_ms, col_score_ms, total_ms).
    preprocess_ms = build_jaccard_column_map + build_aligned_dataframe
    fd_ms         = relative_csv_score (FD mining)
    col_score_ms  = _compute_column_scores
    """
    if df_gen is None or df_gt is None or len(df_gen) == 0:
        return None, None, None, None, None

    df_gen = df_gen.drop(columns=[c for c in df_gen.columns if c.startswith("Unnamed:")], errors="ignore")
    df_gt2 = df_gt.drop(columns=[c for c in df_gt.columns  if c.startswith("Unnamed:")], errors="ignore")

    t0 = time.perf_counter()
    col_map   = vb.build_jaccard_column_map(df_gen, df_gt2)
    df_aligned = vb.build_aligned_dataframe(df_gen, col_map)
    t1 = time.perf_counter()
    preprocess_ms = round((t1 - t0) * 1000, 1)

    t2 = time.perf_counter()
    fd_ratio, col_ratio, combined, fd_f1, _, _ = relative_csv_score(df_aligned, df_gt2)
    t3 = time.perf_counter()
    fd_ms = round((t3 - t2) * 1000, 1)

    t4 = time.perf_counter()
    pairs = [(c, c) for c in df_gt2.columns if c in df_aligned.columns]
    col_scores = vb._compute_column_scores(df_aligned, df_gt2, pairs, col_map)
    t5 = time.perf_counter()
    col_score_ms = round((t5 - t4) * 1000, 1)

    avg_cs = col_scores.get("avg_column_score")
    true_combined = round((fd_f1 + avg_cs) / 2, 4) if avg_cs is not None else round(fd_f1, 4)
    total_ms = round((t5 - t0) * 1000, 1)

    # Per-type averages
    per_col = col_scores.get("per_column", {})
    num_scores = [v["column_score"] for v in per_col.values() if v.get("type") == "numeric"]
    cat_scores = [v["column_score"] for v in per_col.values() if v.get("type") == "categorical"]
    avg_numeric     = round(sum(num_scores) / len(num_scores), 4) if num_scores else None
    avg_categorical = round(sum(cat_scores) / len(cat_scores), 4) if cat_scores else None
    n_numeric_cols  = len(num_scores)
    n_cat_cols      = len(cat_scores)

    return true_combined, preprocess_ms, fd_ms, col_score_ms, total_ms, \
           avg_numeric, avg_categorical, n_numeric_cols, n_cat_cols


def _run_script_and_score(code, gt_path, out_path, split="test", base_split="test"):
    """
    Run a script on the requested split and score it.
    base_split: the split the scripts were originally written for.
      "test"     → scripts reference test_N.csv; sub to training_N.csv when split="training"
      "training" → scripts reference training_N.csv; sub to test_N.csv when split="test"
    Returns (partial, det, preprocess_ms, fd_ms, col_ms, total_ms,
             avg_numeric_det, avg_categorical_det, n_numeric_cols, n_cat_cols, error).
    """
    if base_split == "test":
        if split == "training":
            code = re.sub(r'test_(\d+)\.csv', r'training_\1.csv', code)
        # else split=="test": run as-is
    else:  # base_split == "training"
        if split == "test":
            code = re.sub(r'training_(\d+)\.csv', r'test_\1.csv', code)
        # else split=="training": run as-is

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
        tf.write(code); tmp = tf.name

    try:
        r = subprocess.run(["python3", tmp], capture_output=True, timeout=30, cwd=os.path.abspath("."))
        if r.returncode != 0:
            return *((None,)*10), r.stderr.decode()[:150].strip()
        if not os.path.exists(out_path):
            return *((None,)*10), "no output file"

        df_out = pd.read_csv(out_path, low_memory=False)
        df_gt  = pd.read_csv(gt_path,  low_memory=False)
        df_gt  = df_gt.drop(columns=df_gt.columns[0], axis=1)

        # partial
        try:
            partial, _ = compare_tables_fuzzy(df_out, df_gt)
        except Exception:
            partial = None

        # det_score with timing + per-type scores
        try:
            det, pre_ms, fd_ms, col_ms, tot_ms, avg_num, avg_cat, n_num, n_cat = \
                _timed_det_score(df_out, df_gt)
        except Exception:
            det = pre_ms = fd_ms = col_ms = tot_ms = avg_num = avg_cat = n_num = n_cat = None

        return partial, det, pre_ms, fd_ms, col_ms, tot_ms, avg_num, avg_cat, n_num, n_cat, None

    except subprocess.TimeoutExpired:
        return *((None,)*10), "timeout"
    except Exception as e:
        return *((None,)*10), str(e)[:100]
    finally:
        try: os.unlink(tmp)
        except: pass


# ── Per-case worker (called in Pool) ─────────────────────────────────────────

def _make_script_row(case_id, length, case_is_correct, case_logged_best, n_total,
                     script_idx, logged_test_partial, is_final,
                     split_results_test, split_results_train):
    """Build one script-level row dict from scored results."""
    def _f(v): return round(v, 4) if v is not None else None

    p_te, d_te, pre_te, fd_te, col_te, tot_te, num_te, cat_te, nnum_te, ncat_te, err_te = split_results_test
    p_tr, d_tr, pre_tr, fd_tr, col_tr, tot_tr, num_tr, cat_tr, nnum_tr, ncat_tr, err_tr = split_results_train

    return {
        # Identity
        "case_id":                case_id,
        "length":                 length,
        "case_is_correct":        case_is_correct,
        "case_logged_best_test":  case_logged_best,
        "n_scripts_in_case":      n_total,
        "script_idx":             script_idx,
        "logged_test_partial":    logged_test_partial,  # from execute_and_score in log
        "is_final_script":        is_final,             # matches python_recovered_mcts.py
        # Test split
        "partial_test":           _f(p_te),
        "det_test":               _f(d_te),
        "det_numeric_test":       _f(num_te),
        "det_categorical_test":   _f(cat_te),
        "n_numeric_cols":         nnum_te,
        "n_cat_cols":             ncat_te,
        "preprocess_ms_test":     pre_te,
        "fd_ms_test":             fd_te,
        "col_ms_test":            col_te,
        "total_det_ms_test":      tot_te,
        "error_test":             err_te,
        # Train split
        "partial_train":          _f(p_tr),
        "det_train":              _f(d_tr),
        "det_numeric_train":      _f(num_tr),
        "det_categorical_train":  _f(cat_tr),
        "preprocess_ms_train":    pre_tr,
        "fd_ms_train":            fd_tr,
        "col_ms_train":           col_tr,
        "total_det_ms_train":     tot_tr,
        "error_train":            err_tr,
    }


def process_case(args):
    """
    args = (length, case_id, case_is_correct, logged_best_score,
            final_code, all_scripts, gt_path, out_path)
    Returns a LIST of script-level row dicts (one per script).
    Scripts run sequentially (shared output file); cases run in parallel via Pool.
    """
    import sys
    sys.path.insert(0, ".")
    length, case_id, case_is_correct, logged_best_score, final_code, all_scripts, gt_path, out_path, base_split = args

    # Normalise final script content for identity matching
    final_code_stripped = final_code.strip() if final_code else None

    # Build combined list: log scripts + final if not already present
    # Each entry: (script_idx, logged_test_partial, code, is_final)
    entries = []
    final_found_in_log = False
    for idx, logged_partial, code in all_scripts:
        is_final = (final_code_stripped is not None and code.strip() == final_code_stripped)
        if is_final:
            final_found_in_log = True
        entries.append((idx, logged_partial, code, is_final))

    # If python_recovered_mcts.py didn't match any log script, append it separately
    if not final_found_in_log and final_code_stripped:
        entries.append((len(entries) + 1, None, final_code, True))

    # If no scripts at all, return a single error row
    if not entries:
        none11 = (None,) * 11
        return [_make_script_row(
            case_id, length, case_is_correct, logged_best_score, 0,
            0, None, False, none11, none11
        )]

    n_total = len(entries)
    rows = []

    for script_idx, logged_partial, code, is_final in entries:
        res_te = _run_script_and_score(code, gt_path, out_path, "test")
        res_tr = _run_script_and_score(code, gt_path, out_path, "training")
        rows.append(_make_script_row(
            case_id, length, case_is_correct, logged_best_score, n_total,
            script_idx, logged_partial, is_final, res_te, res_tr
        ))

    return rows


# ── Load all cases ────────────────────────────────────────────────────────────

def load_cases(lengths, log_dirs_by_len, res_dirs_by_len):
    """Return list of case dicts with length, case_id, is_correct, best_score, log_dirs."""
    seen = {}  # case_id → (row, timestamp) — keep latest result per case
    cases_meta = {}  # case_id → log_dirs

    for L in lengths:
        for result_dir in res_dirs_by_len.get(L, []):
            csv_path = os.path.join(result_dir, "results_summary.csv")
            if not os.path.exists(csv_path):
                continue
            with open(csv_path) as fh:
                for row in csv.DictReader(fh):
                    cid = row["case_id"]
                    ts  = row.get("timestamp", "")
                    if cid not in seen or ts > seen[cid][1]:
                        seen[cid] = (row, ts)
                        cases_meta[cid] = (L, log_dirs_by_len.get(L, []))

    cases = []
    for cid, (row, _) in seen.items():
        L, ldirs = cases_meta[cid]
        cases.append({
            "length":     L,
            "case_id":    cid,
            "is_correct": row["is_correct"] == "True",
            "best_score": row.get("best_score", "N/A"),
            "log_dirs":   ldirs,
        })
    return sorted(cases, key=lambda c: (c["length"], c["case_id"]))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", choices=["partial", "score"], default="partial",
                        help="Which experiment to analyse: 'partial' or 'score'")
    parser.add_argument("--lengths", nargs="+", type=int, default=None,
                        help="Lengths to analyse (default: all for chosen experiment)")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", default=None)
    parser.add_argument("--limit", type=int, default=None, help="Limit to first N cases (for testing)")
    parser.add_argument("--cases", nargs="+", default=None,
                        help="Run only these specific case IDs, e.g. --cases 1_22 1_41 1_90")
    args = parser.parse_args()

    # Defaults per experiment
    default_lengths = {"partial": [1, 5], "score": [1, 4, 9]}
    if args.lengths is None:
        args.lengths = default_lengths[args.experiment]
    if args.out is None:
        args.out = f"results_{args.experiment}_analysis.csv"

    log_dirs_by_len, res_dirs_by_len, base_split = get_experiment_config(args.experiment)
    cases = load_cases(args.lengths, log_dirs_by_len, res_dirs_by_len)
    if args.cases:
        cases = [c for c in cases if c["case_id"] in args.cases]
    elif args.limit:
        cases = cases[:args.limit]
    print(f"Total cases: {len(cases)}  (lengths={args.lengths})")
    correct = sum(1 for c in cases if c["is_correct"])
    print(f"  Correct: {correct}  Incorrect: {len(cases) - correct}")

    # Build worker args
    worker_args = []
    for c in cases:
        L, case_id = c["length"], c["case_id"]
        case_num = case_id.split("_")[1]
        data_dir = f"{DATA_BASE}/length{L}_{case_num}"
        gt_path  = f"{data_dir}/target.csv"
        out_path = f"{data_dir}/target_multisource_mcts.csv"

        if not os.path.exists(gt_path):
            print(f"  [SKIP] {case_id}: no target.csv")
            continue

        # Final script
        rec_path = f"{data_dir}/python_recovered_mcts.py"
        if os.path.exists(rec_path):
            final_code = open(rec_path).read()
        else:
            # Fallback: last script from log
            log_path = find_log(L, case_num, c["log_dirs"])
            if log_path and os.path.exists(log_path):
                scripts = extract_scripts_from_log(log_path)
                final_code = scripts[-1][2] if scripts else None
            else:
                final_code = None

        # All scripts from log (for analysis)
        log_path = find_log(L, case_num, c["log_dirs"])
        all_scripts = []
        if log_path and os.path.exists(log_path):
            all_scripts = extract_scripts_from_log(log_path)

        worker_args.append((
            L, case_id, c["is_correct"], c["best_score"],
            final_code, all_scripts, gt_path, out_path, base_split
        ))

    print(f"\nRunning {len(worker_args)} cases with {args.workers} workers  "
          f"(one row per script in output)...")
    print(f"Results appended to: {args.out}\n")

    all_script_rows = []
    cases_done = 0
    total_rows_written = 0
    csv_writer = None
    csv_fh = None

    try:
        with Pool(processes=args.workers) as pool:
            for script_rows in pool.imap_unordered(process_case, worker_args, chunksize=1):
                cases_done += 1

                # ── Open CSV and write header on first batch ──────────────────
                if csv_writer is None and script_rows:
                    fieldnames = list(script_rows[0].keys())
                    csv_fh = open(args.out, "w", newline="")
                    csv_writer = csv.DictWriter(csv_fh, fieldnames=fieldnames)
                    csv_writer.writeheader()
                    csv_fh.flush()

                # ── Append rows immediately and flush ─────────────────────────
                if csv_writer and script_rows:
                    csv_writer.writerows(script_rows)
                    csv_fh.flush()
                    total_rows_written += len(script_rows)

                # ── Progress line ─────────────────────────────────────────────
                final_row = next((r for r in script_rows if r["is_final_script"]), script_rows[0])
                print(f"  [{cases_done:>3}/{len(worker_args)}] {final_row['case_id']:>6}"
                      f"  correct={str(final_row['case_is_correct']):>5}"
                      f"  n_scripts={len(script_rows):>3}"
                      f"  final: partial_te={str(final_row['partial_test']):>6}"
                      f"  partial_tr={str(final_row['partial_train']):>6}"
                      f"  det_te={str(final_row['det_test']):>6}"
                      f"  num_te={str(final_row['det_numeric_test']):>6}"
                      f"  cat_te={str(final_row['det_categorical_test']):>6}"
                      f"  fd_ms={str(final_row['fd_ms_test']):>7}"
                      f"  [csv rows: {total_rows_written}]")

                all_script_rows.extend(script_rows)

    finally:
        if csv_fh:
            csv_fh.close()

    if not all_script_rows:
        print("No results to write.")
        return

    print(f"\nCSV complete: {args.out}  ({total_rows_written} rows)")

    # ── Print analysis summary (case-level, derived from script rows) ──────────
    def safe_mean(vals):
        v = [x for x in vals if x is not None]
        return round(sum(v) / len(v), 4) if v else "N/A"

    print("\n" + "=" * 70)
    print(f"ANALYSIS SUMMARY  (experiment={args.experiment})")
    print("=" * 70)

    for L in args.lengths:
        # Case-level view: use only the final script row per case
        l_rows   = [r for r in all_script_rows if r["length"] == L]
        final_rows = [r for r in l_rows if r["is_final_script"]]
        # Fallback: if no final flagged, use the first script per case
        seen = set()
        if not final_rows:
            for r in l_rows:
                if r["case_id"] not in seen:
                    final_rows.append(r); seen.add(r["case_id"])

        correct_final   = [r for r in final_rows if r["case_is_correct"]]
        incorrect_final = [r for r in final_rows if not r["case_is_correct"]]
        n_cases = len(final_rows)

        print(f"\nLength {L}: {n_cases} cases  "
              f"({len(correct_final)} correct, {len(incorrect_final)} incorrect)  "
              f"| {len(l_rows)} total script rows")

        print(f"  Final script scores (mean across cases):")
        print(f"    partial_test          = {safe_mean([r['partial_test']          for r in final_rows])}")
        print(f"    partial_train         = {safe_mean([r['partial_train']         for r in final_rows])}")
        print(f"    det_test              = {safe_mean([r['det_test']              for r in final_rows])}")
        print(f"    det_train             = {safe_mean([r['det_train']             for r in final_rows])}")
        print(f"    det_numeric_test      = {safe_mean([r['det_numeric_test']      for r in final_rows])}  (numeric cols only)")
        print(f"    det_numeric_train     = {safe_mean([r['det_numeric_train']     for r in final_rows])}  (numeric cols only)")
        print(f"    det_categorical_test  = {safe_mean([r['det_categorical_test']  for r in final_rows])}  (categorical cols only)")
        print(f"    det_categorical_train = {safe_mean([r['det_categorical_train'] for r in final_rows])}  (categorical cols only)")

        print(f"  Timing (mean ms, test split, final scripts):")
        print(f"    preprocess_ms  = {safe_mean([r['preprocess_ms_test'] for r in final_rows])}")
        print(f"    fd_ms          = {safe_mean([r['fd_ms_test']         for r in final_rows])}")
        print(f"    col_score_ms   = {safe_mean([r['col_ms_test']        for r in final_rows])}")
        print(f"    total_det_ms   = {safe_mean([r['total_det_ms_test']  for r in final_rows])}")

        # Better-script analysis: per case, does any non-final script beat the final?
        beats_test_cases  = []
        beats_train_cases = []
        for case_id in {r["case_id"] for r in l_rows}:
            case_scripts = [r for r in l_rows if r["case_id"] == case_id]
            final_s = next((r for r in case_scripts if r["is_final_script"]), None)
            if final_s is None:
                continue
            other_s = [r for r in case_scripts if not r["is_final_script"]]
            # Test
            if final_s["partial_test"] is not None:
                if any(r["partial_test"] is not None and r["partial_test"] > final_s["partial_test"] + 1e-4
                       for r in other_s):
                    beats_test_cases.append(case_id)
            # Train
            if final_s["partial_train"] is not None:
                if any(r["partial_train"] is not None and r["partial_train"] > final_s["partial_train"] + 1e-4
                       for r in other_s):
                    beats_train_cases.append(case_id)

        print(f"\n  'Better script' analysis (all scripts evaluated):")
        print(f"    Cases where another script had HIGHER test partial:  "
              f"{len(beats_test_cases)}/{n_cases}  {beats_test_cases}")
        print(f"    Cases where another script had HIGHER train partial: "
              f"{len(beats_train_cases)}/{n_cases}  {beats_train_cases}")

    print("\n" + "=" * 70)
    print(f"Full results saved to: {args.out}")


if __name__ == "__main__":
    main()
