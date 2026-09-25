"""
Analyze timeout/timeout_recovered cases from rag_det_score_l149.
Extract ALL scripts from ```python``` fences (Tier 2 + Tier 3 cases),
then validate each script using 7 parallel workers via a shared job queue.
As a worker finishes one script it immediately picks up the next.

Usage:
    python3 analyze_timeout_scripts.py [--workers N]
Run from: ~/transchema/
"""

import glob, csv, re, os, sys, tempfile, subprocess, argparse
from multiprocessing import Pool
sys.path.insert(0, ".")

from validation.hard_match import compare_tables_matching
import pandas as pd


RESULTS_BASE = "Langraph/results_langraph/rag_det_score_l149"
LOG_BASE     = "logs_langraph/rag_det_score_l149"
DATA_BASE    = "autopipeline-benchmarks/github-pipelines"


# ── 1. Load timeout cases ─────────────────────────────────────────────────────
def load_timeout_cases():
    timeout_cases = {}
    for f in glob.glob(f"{RESULTS_BASE}/**/results_summary.csv", recursive=True):
        with open(f) as fh:
            for row in csv.DictReader(fh):
                cid, s = row["case_id"], row.get("status", "")
                if s in ("timeout", "timeout_recovered"):
                    if cid not in timeout_cases or row.get("timestamp","") > timeout_cases[cid]["ts"]:
                        timeout_cases[cid] = {"status": s, "ts": row.get("timestamp","")}
    return timeout_cases


# ── 2. Find most recent log per case ──────────────────────────────────────────
def find_case_logs(timeout_cases, subdir_filter=None):
    case_logs = {}
    for f in glob.glob(f"{LOG_BASE}/**/*.log", recursive=True):
        if subdir_filter and subdir_filter not in f:
            continue
        m = re.search(r"(\d+)_target(\d+)_MCTS_(\d+_\d+)\.log", f)
        if not m: continue
        l, cid_num, ts = int(m.group(1)), int(m.group(2)), m.group(3)
        key = f"{l}_{cid_num}"
        if key in timeout_cases:
            if key not in case_logs or ts > case_logs[key][1]:
                case_logs[key] = (f, ts)
    return case_logs


# ── 3. Extract all (script, score) pairs from ```python fences ───────────────
def extract_scripts(log_path):
    """Return list of (script_code, score) tuples.
    Score is taken from the execute_and_score reward line after the closing fence.
    Score is None if no reward line is found (Tier 2 cases).
    """
    lines   = open(log_path).readlines()
    pairs   = []
    buf     = []
    in_s    = False
    for i, line in enumerate(lines):
        if re.match(r"^```[Pp]ython\s*$", line.strip()):
            buf = []; in_s = True; continue
        if in_s:
            if line.strip() == "```":
                code = "".join(buf).strip()
                if code:
                    score = None
                    for j in range(i + 1, min(i + 25, len(lines))):
                        m = re.search(r"execute_and_score.*reward=([\d.]+)", lines[j])
                        if m: score = float(m.group(1)); break
                    pairs.append((code, score))
                in_s = False; buf = []
            else:
                buf.append(line)
    return pairs


# ── 4. Worker: validate one script (called in subprocess) ─────────────────────
def validate_job(job):
    """
    job = (case_id, script_idx, total_scripts, script_code, score, length, cid_num)
    Returns (case_id, script_idx, total_scripts, score, is_correct).
    Runs in a worker process — must not share state with main process.
    """
    import sys, os, re, tempfile, subprocess
    sys.path.insert(0, ".")
    from validation.hard_match import compare_tables_matching
    import pandas as pd

    case_id, script_idx, total_scripts, script_code, score, length, cid_num = job

    # Replace training_N.csv → test_N.csv so scripts validate against test data
    import re as _re
    script_code = _re.sub(r'training_(\d+)\.csv', r'test_\1.csv', script_code)

    gt_file = f"{DATA_BASE}/length{length}_{cid_num}/target.csv"
    if not os.path.exists(gt_file):
        return case_id, script_idx, total_scripts, score, False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir="/tmp") as tf:
        tf.write(script_code)
        tmp_path = tf.name

    try:
        r = subprocess.run(["python3", tmp_path], capture_output=True, timeout=30, cwd=os.getcwd())
        if r.returncode != 0:
            return case_id, script_idx, total_scripts, score, False

        out_file = f"{DATA_BASE}/length{length}_{cid_num}/target_multisource_mcts.csv"
        if not os.path.exists(out_file):
            return case_id, script_idx, total_scripts, score, False

        df_out = pd.read_csv(out_file, low_memory=False)
        df_gt  = pd.read_csv(gt_file, low_memory=False)
        df_gt  = df_gt.drop(columns=df_gt.columns[0], axis=1)
        _, is_correct, _, _ = compare_tables_matching(df_out, df_gt)
        return case_id, script_idx, total_scripts, score, is_correct

    except Exception:
        return case_id, script_idx, total_scripts, score, False
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


# ── 5. Main ───────────────────────────────────────────────────────────────────
def main():
    global RESULTS_BASE, LOG_BASE

    parser = argparse.ArgumentParser()
    parser.add_argument("--workers",     type=int, default=7,   help="Number of parallel workers")
    parser.add_argument("--results_dir", type=str, default=RESULTS_BASE,
                        help="Results base directory to scan for results_summary.csv")
    parser.add_argument("--log_dir",     type=str, default=LOG_BASE,
                        help="Log base directory to scan for MCTS log files")
    parser.add_argument("--all_cases",   action="store_true",
                        help="Analyze ALL cases in log_dir, not just timeout ones")
    parser.add_argument("--output",      type=str, default="timeout_script_analysis_results.csv",
                        help="Output CSV file path")
    args = parser.parse_args()

    RESULTS_BASE = args.results_dir
    LOG_BASE     = args.log_dir

    if args.all_cases:
        # Build case set directly from log files in log_dir (supports glob patterns)
        timeout_cases = {}
        for f in glob.glob(f"{LOG_BASE}/**/*.log", recursive=True) + glob.glob(f"{LOG_BASE}/*.log"):
            m = re.search(r"(\d+)_target(\d+)_MCTS_", f)
            if m:
                key = f"{m.group(1)}_{m.group(2)}"
                if key not in timeout_cases:
                    timeout_cases[key] = {"status": "rerun", "ts": ""}
    else:
        timeout_cases = load_timeout_cases()

    subdir_filter = "cases_rerun2_" if args.all_cases else None
    case_logs = find_case_logs(timeout_cases, subdir_filter=subdir_filter)

    # Build job list: all scripts from Tier 2 + Tier 3 cases
    jobs = []
    skipped_tier1 = 0
    all_scores_by_case = {}
    for case_id, (log_path, _) in sorted(case_logs.items()):
        lines     = open(log_path).readlines()
        has_fence = any(re.match(r"^```[Pp]ython\s*$", l.strip()) for l in lines)
        if not has_fence:
            skipped_tier1 += 1
            continue
        pairs = extract_scripts(log_path)
        l, cid_num = int(case_id.split("_")[0]), int(case_id.split("_")[1])
        all_scores_by_case[case_id] = [s for _, s in pairs if s is not None]
        for idx, (script, score) in enumerate(pairs, 1):
            jobs.append((case_id, idx, len(pairs), script, score, l, cid_num))

    print(f"Cases:                  {len(case_logs) - skipped_tier1}")
    print(f"Total scripts to check: {len(jobs)}")
    print(f"Workers:                {args.workers}")
    print()

    # Track results per case: correct_by_case[case_id] = (script_idx, total, score)
    correct_by_case = {}
    done = 0

    with Pool(processes=args.workers) as pool:
        for case_id, script_idx, total_scripts, score, is_correct in pool.imap_unordered(validate_job, jobs):
            done += 1
            status = "✓ CORRECT" if is_correct else "✗"
            print(f"  [{done:>4}/{len(jobs)}] {case_id} script #{script_idx}/{total_scripts} score={score} → {status}")

            if is_correct:
                if case_id not in correct_by_case or script_idx < correct_by_case[case_id][0]:
                    correct_by_case[case_id] = (script_idx, total_scripts, score)

    # ── Compute rank and highest score per case ───────────────────────────────
    rows = []
    for cid in sorted(correct_by_case):
        idx, total, correct_score = correct_by_case[cid]
        all_scores = sorted([s for s in all_scores_by_case.get(cid, []) if s is not None], reverse=True)
        highest    = all_scores[0] if all_scores else None
        # dense rank: how many unique scores are higher than correct_score
        rank = sum(1 for s in set(all_scores) if s > (correct_score or -1)) + 1
        rows.append({
            "case_id":        cid,
            "status":         timeout_cases[cid]["status"],
            "correct_script": idx,
            "total_scripts":  total,
            "correct_score":  correct_score if correct_score is not None else "N/A",
            "highest_score":  highest if highest is not None else "N/A",
            "rank":           rank,
            "total_unique_scores": len(set(all_scores)),
        })

    # ── Print report ──────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"Total scripts validated:      {done}")
    print(f"Cases with a correct script:  {len(rows)}")
    print(f"Cases with no correct script: {len(case_logs) - skipped_tier1 - len(rows)}")

    if rows:
        hdr = f"{'Case':>8}  {'Status':>20}  {'Script#':>8}  {'CorrectScore':>13}  {'HighestScore':>13}  {'Rank':>5}  {'UniqueScores':>12}"
        print(f"\n{hdr}")
        print("-" * len(hdr))
        for r in rows:
            print(f"{r['case_id']:>8}  {r['status']:>20}  {r['correct_script']:>8}  "
                  f"{str(r['correct_score']):>13}  {str(r['highest_score']):>13}  "
                  f"{r['rank']:>5}  {r['total_unique_scores']:>12}")

    # ── Write CSV ─────────────────────────────────────────────────────────────
    csv_path = args.output if hasattr(args, "output") and args.output else "timeout_script_analysis_results.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys() if rows else [])
        if rows:
            w.writeheader()
            w.writerows(rows)
    print(f"\nCSV written to: {csv_path}")


if __name__ == "__main__":
    main()
