#!/usr/bin/env python3
"""
Verify extracted MS codes from JSON files by executing them and comparing
output against ground truth. Reports accuracy, avg cost, avg latency grouped
by (pipeline_length, model).

Usage:
    python verify_extracted_codes.py          # all lengths
    python verify_extracted_codes.py --len 1  # L1 only
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from validation.hard_match import compare_tables_matching

BASE_LOG_DIR = "logs-auto-suggest-llm-21-04"
SCRIPT_TIMEOUT = 120  # seconds per script


def model_from_dir(dirname):
    """Extract model label from experiment directory name."""
    # e.g. l1_o4mini_ms_mat_... → o4mini
    #      l1_4.1mini_ms_mat_...  → 4.1mini
    m = re.match(r"(?:mp_)?l\d+_([^_]+)_ms_mat", dirname)
    return m.group(1) if m else "unknown"


def length_from_dir(dirname):
    """Extract pipeline length from experiment directory name."""
    m = re.match(r"(?:mp_)?l(\d+)_", dirname)
    return int(m.group(1)) if m else -1


def benchmark_from_dir(dirname):
    return "monteprep" if dirname.startswith("mp_") else "github"


def gt_path(case_id, benchmark):
    base = (
        "autopipeline-benchmarks/monteprep-pipelines"
        if benchmark == "monteprep"
        else "autopipeline-benchmarks/github-pipelines"
    )
    return f"{base}/length{case_id}/target.csv"


def output_path(case_id, benchmark):
    base = (
        "autopipeline-benchmarks/monteprep-pipelines"
        if benchmark == "monteprep"
        else "autopipeline-benchmarks/github-pipelines"
    )
    return f"{base}/length{case_id}/target_multisource.csv"


def critique_output_path(case_id, benchmark):
    base = (
        "autopipeline-benchmarks/monteprep-pipelines"
        if benchmark == "monteprep"
        else "autopipeline-benchmarks/github-pipelines"
    )
    return f"{base}/length{case_id}/target_multisource_critique_history.csv"


def run_code(code, timeout=SCRIPT_TIMEOUT):
    """
    Execute Python code string in a subprocess.
    Returns (success: bool, elapsed: float, error: str).
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tf:
        tf.write(code)
        tf_path = tf.name
    try:
        t0 = time.time()
        result = subprocess.run(
            [sys.executable, tf_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(__file__) or ".",
        )
        elapsed = time.time() - t0
        success = result.returncode == 0
        err = result.stderr.strip() if not success else ""
        return success, elapsed, err
    except subprocess.TimeoutExpired:
        return False, timeout, "TIMEOUT"
    except Exception as e:
        return False, 0.0, str(e)
    finally:
        os.unlink(tf_path)


def hard_match(output_csv, gt_csv):
    """Return True if output matches ground truth via compare_lists_matching."""
    try:
        df_out = pd.read_csv(output_csv, low_memory=False)
        df_gt  = pd.read_csv(gt_csv,     low_memory=False)
        df_gt.drop(columns=df_gt.columns[0], axis=1, inplace=True)
        _, is_correct, _, _ = compare_tables_matching(df_out, df_gt)
        return bool(is_correct)
    except Exception:
        return False


# ---------------------------------------------------------------------------

def run_experiment_dir(exp_dir, target_len=None):
    """
    Execute all MS codes in exp_dir/jsons/*.json.
    Returns list of dicts with per-case results.
    """
    dirname   = os.path.basename(exp_dir)
    model     = model_from_dir(dirname)
    length    = length_from_dir(dirname)
    benchmark = benchmark_from_dir(dirname)

    if target_len is not None and length != target_len:
        return []

    jsons_dir = os.path.join(exp_dir, "jsons")
    if not os.path.isdir(jsons_dir):
        return []

    records = []
    json_paths = sorted(glob.glob(os.path.join(jsons_dir, "*.json")))
    print(f"  [{dirname}] {len(json_paths)} cases …", flush=True)

    for jp in json_paths:
        with open(jp) as f:
            d = json.load(f)

        case_id  = d["case"]
        ms       = d["iterations"][0]["ms"]
        code     = ms.get("code", "")
        csv_cost = ms.get("cost", 0.0)
        csv_lat  = ms.get("latency", 0.0)

        if not code:
            records.append({
                "case": case_id, "model": model, "length": length,
                "benchmark": benchmark,
                "exec_ok": False, "is_correct": False,
                "exec_time": 0.0, "cost": csv_cost, "latency": csv_lat,
                "error": "empty code",
            })
            continue

        exec_ok, exec_time, err = run_code(code)

        gt_csv  = gt_path(case_id, benchmark)
        ms_out  = output_path(case_id, benchmark)
        correct = exec_ok and os.path.exists(ms_out) and hard_match(ms_out, gt_csv)

        # Run critique codes in order; stop as soon as one is correct
        critiques = d["iterations"][0].get("critiques", [])
        crit_correct = False
        for crit in critiques:
            crit_code = crit.get("code", "")
            if not crit_code:
                continue
            crit_ok, _, _ = run_code(crit_code)
            crit_out = critique_output_path(case_id, benchmark)
            if crit_ok and os.path.exists(crit_out) and hard_match(crit_out, gt_csv):
                crit_correct = True
                break

        final_correct = correct or crit_correct

        records.append({
            "case":       case_id,
            "model":      model,
            "length":     length,
            "benchmark":  benchmark,
            "exec_ok":    exec_ok,
            "ms_correct": correct,
            "is_correct": final_correct,
            "exec_time":  exec_time,
            "cost":       csv_cost,
            "latency":    csv_lat,
            "error":      err if not exec_ok else "",
        })

        status = "OK" if final_correct else ("EXEC_FAIL" if not exec_ok else "WRONG")
        print(f"    {case_id}: {status} (ms={correct}, crit={crit_correct})", flush=True)

    # Per-directory accuracy log after all cases in this dir are done
    total      = len(records)
    ms_cor     = sum(1 for r in records if r.get("ms_correct", False))
    final_cor  = sum(1 for r in records if r["is_correct"])
    exec_fail  = sum(1 for r in records if not r["exec_ok"])
    avg_cost   = sum(r["cost"]    for r in records) / total if total else 0.0
    avg_lat    = sum(r["latency"] for r in records) / total if total else 0.0
    print(
        f"\n  >> [{dirname}] DONE — "
        f"MS correct: {ms_cor}/{total}, "
        f"Final (MS+crit): {final_cor}/{total} ({100*final_cor/total:.1f}%), "
        f"Exec failures: {exec_fail}, "
        f"AvgCost: {avg_cost:.4f}, AvgLat: {avg_lat:.2f}s",
        flush=True,
    )

    return records


def summarize(records):
    """Print summary table grouped by (benchmark, length, model)."""
    groups = defaultdict(list)
    for r in records:
        key = (r["benchmark"], r["length"], r["model"])
        groups[key].append(r)

    print("\n" + "=" * 85)
    print(f"{'Benchmark':<12} {'Len':>4} {'Model':<10} "
          f"{'MS_Cor':>7} {'Final':>7} {'Total':>6} {'Acc%':>6} "
          f"{'AvgCost':>10} {'AvgLat(s)':>10}")
    print("=" * 85)

    for key in sorted(groups):
        bench, length, model = key
        recs       = groups[key]
        total      = len(recs)
        ms_correct = sum(1 for r in recs if r.get("ms_correct", False))
        correct    = sum(1 for r in recs if r["is_correct"])
        acc        = 100.0 * correct / total if total else 0.0
        avg_cost   = sum(r["cost"]    for r in recs) / total if total else 0.0
        avg_lat    = sum(r["latency"] for r in recs) / total if total else 0.0
        print(f"{bench:<12} {length:>4} {model:<10} "
              f"{ms_correct:>7} {correct:>7} {total:>6} {acc:>5.1f}% "
              f"{avg_cost:>10.4f} {avg_lat:>10.2f}")

    print("=" * 85)

    # Also list failed executions
    failed = [r for r in records if not r["exec_ok"]]
    if failed:
        print(f"\nExecution failures ({len(failed)}):")
        for r in failed[:20]:
            print(f"  {r['case']}: {r['error'][:80]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--len",  type=int, default=None,
                        help="Only process this pipeline length (e.g. 1)")
    parser.add_argument("--model", type=str, default=None,
                        help="Only process this model (e.g. o4mini or 4.1mini)")
    parser.add_argument("--benchmark", choices=["github", "monteprep"],
                        default=None, help="Filter by benchmark")
    args = parser.parse_args()

    all_records = []
    for name in sorted(os.listdir(BASE_LOG_DIR)):
        if "ms_mat" not in name:
            continue
        if args.model and args.model not in name:
            continue
        if args.benchmark == "github"    and name.startswith("mp_"):
            continue
        if args.benchmark == "monteprep" and not name.startswith("mp_"):
            continue
        exp_dir = os.path.join(BASE_LOG_DIR, name)
        if not os.path.isdir(exp_dir):
            continue
        print(f"\n{name}")
        recs = run_experiment_dir(exp_dir, target_len=args.len)
        all_records.extend(recs)

        # Running aggregate across all dirs processed so far
        if all_records:
            tot = len(all_records)
            fin = sum(1 for r in all_records if r["is_correct"])
            print(
                f"  >> [RUNNING TOTAL] {fin}/{tot} correct ({100*fin/tot:.1f}%)",
                flush=True,
            )

    summarize(all_records)


if __name__ == "__main__":
    main()
