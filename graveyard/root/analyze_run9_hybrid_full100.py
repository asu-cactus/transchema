"""
analyze_run9_hybrid_full100.py
================================
Test the flat LCB-style hybrid selection rule against all 100 run9 L1 cases:

  hybrid_score(script) = score(script) - C / sqrt(freq(rounded_score))

...picked as argmax over EVERY distinct script scored anywhere in that
case's log (no tree-walking -- this sidesteps the "leaf-forcing" bug that
hurts OLD_total_reward/LCB on the tree-path version). freq = how many
separate iterations produced that exact (rounded) score, used as a cheap
confidence/support proxy.

Validates the picked script against TEST data for every case (not just the
36 previously-known-wrong ones), since cases outside that set don't have a
precomputed best_correct_score to compare against.

Runs cases in parallel (ProcessPoolExecutor, 20 workers by default).

Usage: python3 analyze_run9_hybrid_full100.py [--workers N] [--C 0.1]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"
CASES = list(range(100))


def log_dir_for(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


def flat_hybrid_pick(entries, C):
    all_scores = [round(e[3], 4) for e in entries]
    freq_map = {}
    for s in all_scores:
        freq_map[s] = freq_map.get(s, 0) + 1

    seen = {}
    for it, kind, script, score in entries:
        key = script.strip()
        if key not in seen or score > seen[key][1]:
            seen[key] = (script, score)

    best_hybrid, best_script, best_score = -999, None, None
    for key, (script, score) in seen.items():
        r = round(score, 4)
        f = freq_map.get(r, 1)
        hybrid = score - C / math.sqrt(f)
        if hybrid > best_hybrid:
            best_hybrid = hybrid
            best_script = script
            best_score = score
    return best_script, best_score


def process_case(case_num: int, C: float):
    log_dir = log_dir_for(case_num)
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None

    entries = extract_all_scored_scripts(Path(files[-1]))
    if not entries:
        return case_num, {"correct": False, "score": None, "note": "no_scripts"}

    script, score = flat_hybrid_pick(entries, C)
    correct, note = run_and_check(script, case_num)
    return case_num, {"correct": correct, "score": score, "note": note}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--C", type=float, default=0.1)
    args = parser.parse_args()

    results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_case, c, args.C): c for c in CASES}
        for future in as_completed(futures):
            c = futures[future]
            try:
                case_num, info = future.result()
            except Exception as e:
                print(f"c{c} FAILED: {e}", flush=True)
                continue
            results[case_num] = info
            tag = "OK" if info and info.get("correct") else "WRONG"
            print(f"c{case_num} {tag}: {info}", flush=True)

    n = len([r for r in results.values() if r is not None])
    n_ok = sum(1 for r in results.values() if r and r.get("correct"))
    wrong = sorted(c for c, r in results.items() if r is None or not r.get("correct"))
    print(f"\nHYBRID (C={args.C}): {n_ok}/{n} correct")
    print(f"wrong: {wrong}")


if __name__ == "__main__":
    main()
