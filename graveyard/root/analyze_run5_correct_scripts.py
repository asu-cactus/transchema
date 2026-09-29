"""
Analyze run5 training logs:
- Run autopipeline validation on each script (execute + compare_tables_matching)
- Re-score each script using the UPDATED formula (fd_f1 + col_score + row_ratio) / 3
- Check if the new score flips the ranking so the correct script now wins

Usage: python3 analyze_run5_correct_scripts.py
Run from: ~/transchema/
"""
import glob, re, os, sys, csv
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
sys.path.insert(0, ".")

from util.utils import execute_python, make_test_validation_script
from validation.hard_match import compare_tables_matching  # autopipeline validation
from eval_score_value_based import value_based_relative_csv_score_timed

BASE       = "autopipeline-benchmarks/github-pipelines"
LOG_BASE   = "logs_langraph"
RESULTS_LG = "Langraph/results_langraph"

ALL_CASES = {
    1: [9,22,23,24,27,43,50,52,54,56,75,79,86,88,92,95,99],
    4: [16,25,26,27,31,32,36,37,38,40,42,43,55,57,58,67,68,69,71,77,80,82,85,88,90,91],
    9: [2,10,31,32,59,65,82,84,87,89,92,93],
}

LOG_DIRS = {
    1: f"{LOG_BASE}/rag_det_score_run5_l1_training",
    4: f"{LOG_BASE}/rag_det_score_run5_l4_training",
    9: f"{LOG_BASE}/rag_det_score_run5_l9_training",
}


def load_incorrect_cases():
    incorrect = {1: [], 4: [], 9: []}
    for length in [1, 4, 9]:
        for path in sorted(glob.glob(
            f"{RESULTS_LG}/rag_det_score_run5_l{length}_training/*/results_summary.csv"
        )):
            with open(path) as f:
                for row in csv.DictReader(f):
                    cid = int(row["case_id"].split("_")[1])
                    if cid in ALL_CASES[length] and row.get("is_correct") != "True":
                        if cid not in incorrect[length]:
                            incorrect[length].append(cid)
    return incorrect


def extract_scripts_with_scores(logfile):
    content = open(logfile).read()
    iter_pat   = re.compile(r'\[execute_and_score\] Iter \d+: reward=([\d.]+)')
    script_pat = re.compile(r'```(?:[Pp]ython)?\n(.*?)```', re.DOTALL)
    scripts = [(m.start(), m.group(1)) for m in script_pat.finditer(content)
               if 'pd.read_csv' in m.group(1) and 'to_csv' in m.group(1)]
    scores  = [(m.start(), float(m.group(1))) for m in iter_pat.finditer(content)]
    pairs, seen = [], set()
    for s_pos, script in scripts:
        reward = next((r for e_pos, r in scores if e_pos > s_pos), 0.0)
        h = hash(script.strip())
        if h not in seen:
            seen.add(h)
            pairs.append((script, reward))
    return pairs


def run_script_and_score(script, length, case_id, worker_id):
    """
    Score on training output, validate on test output.
    - new_score : computed from training execution (what MCTS would actually see)
    - is_correct: from autopipeline validation on test execution
    """
    gt_path       = f"{BASE}/length{length}_{case_id}/target.csv"
    train_out     = f"{BASE}/length{length}_{case_id}/target_multisource_mcts_w{worker_id}.csv"
    test_out      = f"{BASE}/length{length}_{case_id}/target_multisource_mcts_test_val_w{worker_id}.csv"

    # Build training and test scripts independently from the original
    # to avoid make_test_validation_script mangling the worker-id suffix.
    train_script = re.sub(r'target_multisource_mcts\.csv',
                          f'target_multisource_mcts_w{worker_id}.csv', script)
    test_script_base = make_test_validation_script(script)   # start from original
    test_script  = re.sub(r'target_multisource_mcts_test_val\.csv',
                          f'target_multisource_mcts_test_val_w{worker_id}.csv', test_script_base)

    new_score  = 0.0
    is_correct = False
    try:
        df_gt = pd.read_csv(gt_path, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        # ── Score on training output ──────────────────────────────────────
        if execute_python(train_script) == "Success" and os.path.exists(train_out):
            df_train_out = pd.read_csv(train_out, low_memory=False)
            try:
                res = value_based_relative_csv_score_timed(df_train_out, df_gt, timeout=60)
                new_score = res[4]
            except Exception:
                new_score = 0.0

        # ── Validate on test output ───────────────────────────────────────
        if execute_python(test_script) == "Success" and os.path.exists(test_out):
            df_test_out = pd.read_csv(test_out, low_memory=False)
            _, is_correct, _, _ = compare_tables_matching(df_test_out, df_gt)

    except Exception:
        pass
    finally:
        for p in [train_out, test_out]:
            if os.path.exists(p):
                os.remove(p)

    return is_correct, new_score


def analyze_case(args):
    length, case_id, worker_id = args
    key = f"{length}_{case_id}"

    logfiles = sorted(glob.glob(f"{LOG_DIRS[length]}/cases_c{case_id}/*.log"))
    if not logfiles:
        return key, "missing", None, None, None, None, None, None, None

    pairs = extract_scripts_with_scores(logfiles[-1])
    if not pairs:
        return key, "no_scripts", None, None, None, None, None, None, None

    # Score all scripts with new formula
    scored = []
    for script, old_score in pairs:
        is_correct, new_score = run_script_and_score(script, length, case_id, worker_id)
        scored.append((script, old_score, new_score, is_correct))

    # Old winner: highest old_score
    old_winner = max(scored, key=lambda x: x[1])
    # New winner: highest new_score
    new_winner = max(scored, key=lambda x: x[2])

    # Correct scripts
    correct_entries = [x for x in scored if x[3]]

    if not correct_entries:
        return key, "no_correct_script", old_winner[1], old_winner[2], None, None, new_winner[1], new_winner[2], new_winner[3]

    correct_entry = max(correct_entries, key=lambda x: x[2])  # best correct by new score

    old_flipped = old_winner[3] is False and correct_entries  # old winner was wrong
    new_flipped = new_winner[3] is True  # new winner is correct

    status = "FLIPPED ✓" if (old_flipped and new_flipped) else \
             "still_wrong" if old_flipped else "was_already_correct"

    return (key, status,
            old_winner[1], old_winner[2],           # old winner: old_score, new_score
            correct_entry[1], correct_entry[2],     # correct: old_score, new_score
            new_winner[1], new_winner[2], new_winner[3])  # new winner: old_score, new_score, is_correct


if __name__ == "__main__":
    CASES = load_incorrect_cases()
    total = sum(len(v) for v in CASES.values())
    print(f"Analyzing {total} incorrect cases with new row_ratio score\n")
    print(f"{'Case':<8} {'Status':<22} {'Old winner':^22} {'Correct script':^22} {'New winner (+row)':^26}")
    print(f"{'':8} {'':22} {'old_s':>10} {'new_s':>10}   {'old_s':>10} {'new_s':>10}   {'old_s':>10} {'new_s':>10} {'ok':>4}")
    print(f"{'':8} {'':22} {'(no row)':>10} {'(+row)':>10}   {'(no row)':>10} {'(+row)':>10}   {'(no row)':>10} {'(+row)':>10} {'':>4}")
    print("-" * 105)

    RUN_LENGTHS = [1,4,9]   # ← change here to control which lengths to run

    tasks = [(l, c, i % 20)
             for i, (l, c) in enumerate((l, c) for l in RUN_LENGTHS for c in CASES[l])]

    results = {}
    flipped, still_wrong, no_correct = [], [], []

    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(analyze_case, t): t for t in tasks}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Analyzing cases"):
            r = future.result()
            # Ensure we always have 8 values after key
            vals = list(r[1:])
            while len(vals) < 8:
                vals.append(None)
            results[r[0]] = tuple(vals)

    for length in RUN_LENGTHS:
        for case_id in CASES[length]:
            key = f"{length}_{case_id}"
            if key not in results: continue
            status, ow_old, ow_new, cs_old, cs_new, nw_old, nw_new, nw_ok = results[key]
            ow_old_s = f"{ow_old:.4f}" if ow_old is not None else "—"
            ow_new_s = f"{ow_new:.4f}" if ow_new is not None else "—"
            cs_old_s = f"{cs_old:.4f}" if cs_old is not None else "—"
            cs_new_s = f"{cs_new:.4f}" if cs_new is not None else "—"
            nw_old_s = f"{nw_old:.4f}" if nw_old is not None else "—"
            nw_new_s = f"{nw_new:.4f}" if nw_new is not None else "—"
            nw_ok_s  = "✓" if nw_ok else "✗"
            print(f"{key:<8} {status:<22} {ow_old_s:>10} {ow_new_s:>10}   {cs_old_s:>10} {cs_new_s:>10}   {nw_old_s:>10} {nw_new_s:>10} {nw_ok_s:>4}")
            if "FLIPPED" in status: flipped.append(key)
            elif "still_wrong" in status: still_wrong.append(key)
            elif "no_correct" in status: no_correct.append(key)

    print(f"\n{'='*80}")
    print(f"Rankings FLIPPED by row_ratio : {len(flipped)} — {sorted(flipped)}")
    print(f"Still wrong (correct exists)  : {len(still_wrong)} — {sorted(still_wrong)}")
    print(f"No correct script found       : {len(no_correct)}")
