"""
extract_unique_scored_scripts.py
===================================
For run9's training-split L1/L4/L9 legs, extract every UNIQUE scored script
per case from its MCTS log (deduplicated by script text -- the same script
often reappears across iterations; only keep it once, at its best score) and
dump each to its own .py file.

  L1 -> rag_det_score_run9_l1_pilot20 (0-19) + _batch_20to100 (20-99), training
  L4 -> test_script_4_l4, training
  L9 -> test_script_4_l9, training

Output layout:
  scratchpad/extracted_unique_scripts/l<length>/case_<n>/
    manifest.json                          -- [{rank, score, kind, iter, file}]
    script_<rank>_score_<score>_<kind>.py

Usage: python3 extract_unique_scored_scripts.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts

OUT_ROOT = Path("scratchpad/extracted_unique_scripts")

CONFIGS = [
    (1, None, 100),   # L1 uses log_dir_for() below (pilot/batch split)
    (4, "logs_langraph/test_script_4_l4", 100),
    (9, "logs_langraph/test_script_4_l9", 101),
]

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"


def log_dir_for_l1(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


def dedupe(entries):
    """Keep one entry per unique SCORE (rounded to 4dp) -- not per unique script
    text. Many distinct script texts land on the same score (trivial rewrites,
    reordered ops that are equivalent on this data, etc.), so score is the
    real identity here; the first script seen at a given score is kept as its
    representative."""
    seen = {}
    for it, kind, script, score in entries:
        key = round(score, 4)
        if key not in seen:
            seen[key] = (it, kind, score, script)
    # sort by score descending
    return sorted(seen.values(), key=lambda t: -t[2])


def process_case(length, log_dir, case_num):
    d = log_dir_for_l1(case_num) if length == 1 else log_dir
    files = sorted(glob.glob(f"{d}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, 0
    log_file = Path(files[-1])

    entries = extract_all_scored_scripts(log_file)
    if not entries:
        return length, case_num, 0

    unique = dedupe(entries)

    case_dir = OUT_ROOT / f"l{length}" / f"case_{case_num}"
    case_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for rank, (it, kind, score, script) in enumerate(unique, start=1):
        fname = f"script_{rank}_score_{score:.4f}_{kind}.py"
        (case_dir / fname).write_text(script)
        manifest.append({"rank": rank, "iter": it, "kind": kind, "score": score, "file": fname})

    (case_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return length, case_num, len(unique)


def main():
    tasks = []
    for length, log_dir, n in CONFIGS:
        for c in range(n):
            tasks.append((length, log_dir, c))

    totals = {1: 0, 4: 0, 9: 0}
    counts = {1: 0, 4: 0, 9: 0}
    pbar = tqdm(total=len(tasks), desc="extracting", unit="case")
    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_case, l, d, c): (l, c) for l, d, c in tasks}
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                length_r, case_num, n_unique = future.result()
            except Exception as e:
                pbar.write(f"L{length} c{c} FAILED: {e}")
                pbar.update(1)
                continue
            totals[length] += n_unique
            counts[length] += 1
            pbar.set_postfix(L1=counts[1], L4=counts[4], L9=counts[9])
            pbar.update(1)
    pbar.close()

    print(f"\n{'='*70}\nSummary\n{'='*70}")
    for length, log_dir, n in CONFIGS:
        print(f"L{length}: {counts[length]}/{n} cases processed, "
              f"{totals[length]} unique scripts total "
              f"(avg {totals[length]/max(counts[length],1):.1f}/case) "
              f"-> {OUT_ROOT}/l{length}/")


if __name__ == "__main__":
    main()
