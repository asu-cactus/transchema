"""
Analyze run7 L1 training logs — all incorrect cases:
- For each failed case, extract every unique script from the MCTS log
- Run each script on TEST data via make_test_validation_script
- Validate with compare_tables_matching (autopipeline)
- Report whether the correct script EXISTS in the log, and if so whether
  our new scoring would have ranked it #1

Usage: python3 analyze_run7_l1_correct_scripts.py
Run from: ~/transchema/
"""
import glob, re, os, sys, csv
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
sys.path.insert(0, ".")

from util.utils import execute_python, make_test_validation_script
from validation.hard_match import compare_tables_matching
from eval_score_value_based import value_based_relative_csv_score_timed

BASE       = "autopipeline-benchmarks/github-pipelines"
LOG_BASE   = "logs_langraph"
RESULTS_LG = "Langraph/results_langraph"
RUN_DIR    = "rag_det_score_run7_l1_training"


def load_incorrect_cases():
    incorrect = []
    for path in sorted(glob.glob(f"{RESULTS_LG}/{RUN_DIR}/*/results_summary.csv")):
        with open(path) as f:
            for row in csv.DictReader(f):
                if not row.get("case_id") or row["case_id"] == "case_id":
                    continue
                parts = row["case_id"].split("_")
                if len(parts) != 2: continue
                cid = int(parts[1])
                if row.get("is_correct") != "True" and cid not in incorrect:
                    incorrect.append(cid)
    return sorted(incorrect)


def extract_scripts_with_scores(logfile):
    content = open(logfile).read()
    iter_pat   = re.compile(r'\[execute_and_score\] Iter \d+: reward=([\d.]+)')
    script_pat = re.compile(r'```(?:[Pp]ython)\n(.*?)```', re.DOTALL)
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


def run_script_and_score(script, case_id, worker_id):
    gt_path    = f"{BASE}/length1_{case_id}/target.csv"
    train_out  = f"{BASE}/length1_{case_id}/target_multisource_mcts_w{worker_id}.csv"
    test_out   = f"{BASE}/length1_{case_id}/target_multisource_mcts_recovery_test_val_w{worker_id}.csv"

    train_script = re.sub(
        r'target_multisource_mcts\.csv',
        f'target_multisource_mcts_w{worker_id}.csv', script
    )
    test_script_base = make_test_validation_script(script)
    test_script = test_script_base.replace(
        "target_multisource_mcts_test_val.csv",
        f"target_multisource_mcts_recovery_test_val_w{worker_id}.csv"
    )

    new_score  = 0.0
    is_correct = False
    try:
        df_gt = pd.read_csv(gt_path, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        if execute_python(train_script) == "Success" and os.path.exists(train_out):
            df_train = pd.read_csv(train_out, low_memory=False)
            try:
                res = value_based_relative_csv_score_timed(df_train, df_gt, timeout=30)
                new_score = res[4]
            except Exception:
                new_score = 0.0

        if execute_python(test_script) == "Success" and os.path.exists(test_out):
            df_test = pd.read_csv(test_out, low_memory=False)
            _, is_correct, _, _ = compare_tables_matching(df_test, df_gt)

    except Exception:
        pass
    finally:
        for p in [train_out, test_out]:
            if os.path.exists(p):
                os.remove(p)

    return is_correct, new_score


def analyze_case(args):
    case_id, worker_id = args

    logfiles = sorted(glob.glob(f"{LOG_BASE}/{RUN_DIR}/cases_c{case_id}/*.log"))
    if not logfiles:
        return case_id, "missing_log", None, None, None, None

    pairs = extract_scripts_with_scores(logfiles[-1])
    if not pairs:
        return case_id, "no_scripts", None, None, None, None

    scored = []
    for script, old_score in pairs:
        is_correct, new_score = run_script_and_score(script, case_id, worker_id)
        scored.append((script, old_score, new_score, is_correct))

    old_winner  = max(scored, key=lambda x: x[1])
    new_winner  = max(scored, key=lambda x: x[2])
    correct_entries = [x for x in scored if x[3]]

    if not correct_entries:
        return case_id, "no_correct_script", old_winner[1], old_winner[2], None, None

    best_correct = max(correct_entries, key=lambda x: x[2])

    old_was_wrong  = not old_winner[3]
    new_winner_ok  = new_winner[3]

    if old_was_wrong and new_winner_ok:
        status = "FLIPPED ✓"
    elif old_was_wrong:
        status = "still_wrong"
    else:
        status = "was_already_correct"

    return (case_id, status,
            old_winner[1], old_winner[2],
            best_correct[1], best_correct[2],
            new_winner[1], new_winner[2], new_winner[3])


if __name__ == "__main__":
    incorrect = load_incorrect_cases()
    print(f"Incorrect L1 cases in run7: {len(incorrect)} — {incorrect}\n")

    print(f"{'Case':<8} {'Status':<22} {'Old winner':^22} {'Correct script':^22} {'New winner':^26}")
    print(f"{'':8} {'':22} {'old_s':>10} {'new_s':>10}   {'old_s':>10} {'new_s':>10}   {'old_s':>10} {'new_s':>10} {'ok':>4}")
    print("-" * 110)

    tasks = [(cid, i % 20) for i, cid in enumerate(incorrect)]

    results = {}
    flipped, still_wrong, no_correct = [], [], []

    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(analyze_case, t): t for t in tasks}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Analyzing"):
            r = future.result()
            case_id = r[0]
            vals = list(r[1:])
            while len(vals) < 8:
                vals.append(None)
            results[case_id] = tuple(vals)

    for case_id in incorrect:
        if case_id not in results:
            continue
        row = results[case_id]
        status = row[0]
        if len(row) >= 8 and row[1] is not None:
            ow_old, ow_new, cs_old, cs_new, nw_old, nw_new, nw_ok = row[1:]
            print(f"1_{case_id:<5} {status:<22} {ow_old or 0:>10.4f} {ow_new or 0:>10.4f}   "
                  f"{cs_old or 0:>10.4f} {cs_new or 0:>10.4f}   "
                  f"{nw_old or 0:>10.4f} {nw_new or 0:>10.4f} {'✓' if nw_ok else '✗':>4}")
        else:
            print(f"1_{case_id:<5} {status:<22}")

        if "FLIPPED" in status:  flipped.append(case_id)
        elif "still_wrong" in status: still_wrong.append(case_id)
        elif "no_correct" in status:  no_correct.append(case_id)

    print(f"\n{'='*80}")
    print(f"New scoring FLIPS ranking (correct now wins) : {len(flipped)} — {flipped}")
    print(f"Still wrong (correct exists but doesn't win) : {len(still_wrong)} — {still_wrong}")
    print(f"No correct script found in log              : {len(no_correct)} — {no_correct}")
    total_fixable = len(flipped) + len(still_wrong)
    print(f"Total with correct script in log            : {total_fixable} — could be correct with better scoring/recovery")
