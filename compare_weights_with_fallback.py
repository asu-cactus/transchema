"""
compare_weights_with_fallback.py
===================================
Same equal-weight vs new-weight lookup comparison as
compare_weights_lookup_l4_l9.py, but per user instruction: when a case's
lookup is unresolved (the picked script's score never made it into
score_regression_dataset.csv), DON'T drop the case -- fall back to that
case's REAL validated correctness from the actual July 3 full-execution run
(analyze_test_script_4_all_methods.py --length 4 / --length 9), parsed from
its saved per-case output table. This keeps denominators at the true 86/101
(L4/L9 cases with a completed log) instead of shrinking to whatever the
lookup happens to resolve.

Usage: python3 compare_weights_with_fallback.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_new_weights_all_methods import load_lookup, process_case, METHOD_NAMES, CONFIGS

EQUAL_W = {"fd_f1": 0.25, "avg_col_score_1": 0.25, "row_count_score": 0.25, "max_missing_score": 0.25}
NEW_W = {"fd_f1": 0.1241, "avg_col_score_1": 0.2487, "row_count_score": 0.3562, "max_missing_score": 0.2710}

TARGET_CONFIGS = CONFIGS  # L1, L4, L9

REAL_OUT_FILES = {
    1: "/tmp/claude-969121990/-home-asurite-ad-asu-edu-jrtandel-transchema/5da6060c-7acf-42da-a262-681cf537fac6/scratchpad/real_l1_training_full.out",
    4: "/tmp/claude-969121990/-home-asurite-ad-asu-edu-jrtandel-transchema/5da6060c-7acf-42da-a262-681cf537fac6/scratchpad/real_l4_full.out",
    9: "/tmp/claude-969121990/-home-asurite-ad-asu-edu-jrtandel-transchema/5da6060c-7acf-42da-a262-681cf537fac6/scratchpad/real_l9_full.out",
}

ROW_RE = re.compile(r"^(\d+)\s+(.+)$")
CELL_RE = re.compile(r"([\d.]+|N/A)/(OK|WRONG)")


def parse_real_ground_truth(length):
    """Return {case_num: {method_name: is_match_bool}} from the saved real-run output."""
    path = REAL_OUT_FILES[length]
    text = open(path).read()
    gt = {}
    for line in text.splitlines():
        if line.startswith("NO LOG") or "NO LOG" in line:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        case_num = int(m.group(1))
        cells = CELL_RE.findall(m.group(2))
        if len(cells) != len(METHOD_NAMES):
            continue
        gt[case_num] = {name: (tag == "OK") for name, (score, tag) in zip(METHOD_NAMES, cells)}
    return gt


def run_all(weights):
    lookup = load_lookup(weights=weights)
    tasks = [(length, log_dir, c) for length, log_dir, n in TARGET_CONFIGS for c in range(n)]
    results = {1: {}, 4: {}, 9: {}}
    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_case, l, d, c, lookup): (l, c) for l, d, c in tasks}
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                length_r, case_num, out = future.result()
            except Exception:
                continue
            results[length][case_num] = out
    return results


def summarize_with_fallback(results, ground_truth, length, n):
    row = {}
    for name in METHOD_NAMES:
        n_ok = n_known = 0
        for c in range(n):
            out = results[length].get(c)
            is_match = None
            if out is not None:
                methods, n_miss, n_tot = out
                score, is_match = methods[name]
            if is_match is None:
                # fallback: keep the case's REAL validated correctness for this method
                gt_case = ground_truth.get(c)
                if gt_case is None:
                    continue  # truly no data anywhere (no log at all) -- excluded
                is_match = gt_case[name]
            n_known += 1
            n_ok += bool(is_match)
        row[name] = (n_ok, n_known)
    return row


def main():
    print("Parsing real ground-truth per-case results...", flush=True)
    gt_l1 = parse_real_ground_truth(1)
    gt_l4 = parse_real_ground_truth(4)
    gt_l9 = parse_real_ground_truth(9)
    print(f"L1 ground truth: {len(gt_l1)} cases, L4: {len(gt_l4)} cases, L9: {len(gt_l9)} cases", flush=True)

    print("Running EQUAL-weight lookup pass...", flush=True)
    eq_results = run_all(EQUAL_W)
    print("Running NEW-weight lookup pass...", flush=True)
    new_results = run_all(NEW_W)

    ground_truth = {1: gt_l1, 4: gt_l4, 9: gt_l9}

    for length, log_dir, n in TARGET_CONFIGS:
        gt = ground_truth[length]
        eq_row = summarize_with_fallback(eq_results, gt, length, n)
        new_row = summarize_with_fallback(new_results, gt, length, n)
        print(f"\n{'='*80}\nL{length} -- lookup + real-fallback comparison\n{'='*80}")
        print(f"{'Method':<18}{'Equal-weight':<20}{'New-weight':<20}{'Delta':<10}")
        for name in METHOD_NAMES:
            eo, ek = eq_row[name]
            no, nk = new_row[name]
            print(f"{name:<18}{f'{eo}/{ek}':<20}{f'{no}/{nk}':<20}{no-eo:+d}")


if __name__ == "__main__":
    main()
