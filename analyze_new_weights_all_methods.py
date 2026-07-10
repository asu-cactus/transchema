"""
analyze_new_weights_all_methods.py
=====================================
Recompute all 5 selection methods (BEST_SCORE, OLD_total_reward, Q_VALUE,
LCB_C=0.5, HYBRID_C=0.1) under the NEW pairwise-LR component weights:

  fd_f1=0.1241, avg_col_score_1=0.2487, row_count_score=0.3562, max_missing_score=0.2710

WITHOUT re-running any scripts: reuses the (fd_f1, avg_col_score_1,
row_count_score, max_missing_score, is_match) already computed and cached in
score_regression_dataset.csv. For every scored event in a log (every
iteration's sim/critique score), look up its OLD log_score in that CSV
(keyed by (length, case_num, round(log_score,4))); if found, use its stored
components to compute new_score = w.components, and its stored is_match as
the correctness label for that event. Missing lookups (log_score never made
it into the CSV, e.g. scoring exceptions) fall back to the OLD score
unchanged and are counted/reported separately.

The MCTS tree is reconstructed exactly as eval_run8_training.parse_log_with_scripts
does, except backpropagation uses new_score in place of the original
pre_score/critique_score for total_reward/best tracking -- topology (which
nodes exist, which path each iteration took) is unchanged, only the reward
values injected into it differ.

Usage: python3 analyze_new_weights_all_methods.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import csv
import glob
import math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from eval_run8_training import (
    ReconNode, find_or_create_path, _get_or_create_child, _split_gba, _parse_list,
    _extract_last_code_block, _reset_cur,
    RE_SELECT, RE_EXPAND_ADD, RE_SIMULATE, RE_PIPELINE, RE_SCORE, RE_CRIT_PLAN,
    RE_CRIT_SCORE, RE_CRIT_PATH, RE_BP_DIVERGE, RE_BP_DONE, RE_QUERY_TYPE,
    RE_RESULT_RCV, RE_COST_LINE, get_node_script,
)
from analyze_run8_failed_case_scripts import extract_all_scored_scripts

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]
W = {"fd_f1": 0.1241, "avg_col_score_1": 0.2487, "row_count_score": 0.3562, "max_missing_score": 0.2710}
W_VEC = [W[f] for f in FEATURES]

METHOD_NAMES = ["BEST_SCORE", "OLD_total_reward", "Q_VALUE", "LCB_C=0.5", "HYBRID_C=0.1"]

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"


def log_dir_for_l1(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


CONFIGS = [
    (1, None, 100),
    (4, "logs_langraph/test_script_4_l4", 100),
    (9, "logs_langraph/test_script_4_l9", 101),
]


# ---------------------------------------------------------------------------
# Lookup table: (length, case_num) -> {round(old_score,4): (new_score, is_match)}
# ---------------------------------------------------------------------------

def load_lookup(path="score_regression_dataset.csv", weights=None):
    weights = weights or W
    lookup = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["train_run_ok"] != "True":
                continue
            if any(r[k] == "" for k in FEATURES):
                continue
            key = (r["length"], r["case_num"])
            old_score = round(float(r["log_score"]), 4)
            new_score = sum(weights[f] * float(r[f]) for f in FEATURES)
            is_match = r["is_match"] == "True" if r["is_match"] in ("True", "False") else None
            lookup.setdefault(key, {})[old_score] = (new_score, is_match)
    return lookup


def relook(lookup_case, old_score):
    """(new_score, is_match, found) for one old log_score, with fallback."""
    if lookup_case is None:
        return old_score, None, False
    entry = lookup_case.get(round(old_score, 4))
    if entry is None:
        return old_score, None, False
    new_score, is_match = entry
    return new_score, is_match, True


# ---------------------------------------------------------------------------
# Modified tree parser: substitute new_score at backprop time
# ---------------------------------------------------------------------------

def parse_log_with_new_rewards(filepath: Path, lookup_case):
    text = filepath.read_text(errors="replace")
    lines = text.splitlines()
    root = ReconNode(op="ROOT", cfg="ROOT", depth=0)

    cur = _reset_cur()
    iter_scripts = {}
    global_best_score = float("-inf")
    global_best_script = ""
    global_best_is_match = None

    current_query_type = None
    in_llm_response = False
    response_lines = []

    node_meta = {}  # id(node) -> is_match for node.best
    n_lookup_miss = 0
    n_lookup_total = 0
    total_iters = 0

    def apply_backprop_new(cur):
        nonlocal n_lookup_miss, n_lookup_total
        rollout = cur["rollout_history"] or []
        llm_plan = cur["llm_plan"] or rollout
        pre_score = cur["pre_score"]
        crit_plan = cur["critique_plan"] or []
        crit_cap = cur["critique_cap"]
        crit_score = cur["critique_score"]
        diverged = cur["diverged"]
        n_sel_only = cur["n_sel_only"]
        has_crit = cur["has_critique"]
        it = cur["iter"]

        new_pre, pre_match, pre_found = relook(lookup_case, pre_score)
        new_crit, crit_match, crit_found = relook(lookup_case, crit_score)
        n_lookup_total += 2
        n_lookup_miss += (0 if pre_found else 1) + (0 if crit_found else 1)

        expanded_depth = len(rollout)
        if diverged and llm_plan and expanded_depth > 0:
            sim_path = find_or_create_path(root, llm_plan[:expanded_depth])
        else:
            sim_path = find_or_create_path(root, rollout)

        for node in sim_path:
            node.visits += 1
            node.total_reward += new_pre
            if new_pre > node.best:
                node.best = new_pre
                node.best_iter = it
                node.best_is_critique = False
                node_meta[id(node)] = pre_match

        if diverged and n_sel_only > 0:
            selection_path = find_or_create_path(root, rollout)
            sim_ids = {id(n) for n in sim_path}
            sel_only = [n for n in selection_path if id(n) not in sim_ids]
            for node in sel_only[:n_sel_only]:
                node.visits += 1

        if has_crit and crit_plan and crit_cap > 0:
            crit_path = find_or_create_path(root, crit_plan[:crit_cap])
            for node in crit_path:
                node.visits += 1
                node.total_reward += new_crit
                if new_crit > node.best:
                    node.best = new_crit
                    node.best_iter = it
                    node.best_is_critique = True
                    node_meta[id(node)] = crit_match

        return new_pre, pre_match, pre_found, new_crit, crit_match, crit_found

    for line in lines:
        m = RE_QUERY_TYPE.search(line)
        if m:
            current_query_type = m.group(1)
            in_llm_response = False
            response_lines = []
        elif RE_RESULT_RCV.search(line):
            in_llm_response = True
            response_lines = [line]
        elif RE_COST_LINE.search(line) and in_llm_response:
            in_llm_response = False
            code = _extract_last_code_block(response_lines)
            if code:
                it = cur["iter"]
                if it >= 0:
                    if it not in iter_scripts:
                        iter_scripts[it] = {"sim": None, "critique": None}
                    if current_query_type == "Simulate":
                        iter_scripts[it]["sim"] = code
                    elif current_query_type == "Critique":
                        iter_scripts[it]["critique"] = code
            response_lines = []
        elif in_llm_response:
            response_lines.append(line)

        m = RE_SELECT.search(line)
        if m:
            cur["iter"] = int(m.group(1))
            cur["expand_children"] = []

        m = RE_EXPAND_ADD.search(line)
        if m and cur["iter"] >= 0 and int(m.group(1)) == cur["iter"]:
            cur["expand_children"].append(m.group(2).strip())

        m = RE_SIMULATE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["rollout_history"] = _split_gba(_parse_list(m.group(2)))
            rollout = cur["rollout_history"]
            if rollout:
                parent_node = find_or_create_path(root, rollout[:-1])[-1]
                for cfg_prefix in cur["expand_children"]:
                    _get_or_create_child(parent_node, cfg_prefix)

        m = RE_PIPELINE.search(line)
        if m:
            cur["llm_plan"] = _split_gba(_parse_list(m.group(1)))

        m = RE_SCORE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["pre_score"] = float(m.group(2))
            if cur["rollout_history"] is None:
                cur["rollout_history"] = _split_gba(_parse_list(m.group(3)))

        m = RE_CRIT_PLAN.search(line)
        if m:
            cur["critique_plan"] = _split_gba(_parse_list(m.group(1)))

        m = RE_CRIT_SCORE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["critique_score"] = float(m.group(2))

        m = RE_CRIT_PATH.search(line)
        if m:
            cur["has_critique"] = True
            cur["critique_cap"] = int(m.group(2))

        m = RE_BP_DIVERGE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["diverged"] = True
            cur["n_sel_only"] = int(m.group(2))

        m = RE_BP_DONE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            it = cur["iter"]
            it_sc = iter_scripts.get(it, {})
            sim_sc = it_sc.get("sim") or ""
            crit_sc = it_sc.get("critique") or ""

            new_pre, pre_match, pre_found, new_crit, crit_match, crit_found = apply_backprop_new(cur)

            if new_pre > global_best_score and sim_sc:
                global_best_score = new_pre
                global_best_script = sim_sc
                global_best_is_match = pre_match
            if new_crit > global_best_score and crit_sc:
                global_best_score = new_crit
                global_best_script = crit_sc
                global_best_is_match = crit_match

            total_iters = it + 1
            cur = _reset_cur()

    return (root, iter_scripts, global_best_script, global_best_score, global_best_is_match,
            total_iters, node_meta, n_lookup_miss, n_lookup_total)


# ---------------------------------------------------------------------------
# Path-walking methods (same shape as prior analysis scripts)
# ---------------------------------------------------------------------------

def greedy_tr_path(root):
    path = [root]
    node = root
    while node.children:
        node = max(node.children.values(), key=lambda c: (c.total_reward, c.visits))
        path.append(node)
    return path


def greedy_q_path(root):
    path = [root]
    node = root
    while node.children:
        node = max(node.children.values(),
                    key=lambda c: (c.total_reward / c.visits if c.visits else -1.0, c.visits))
        path.append(node)
    return path


def greedy_path_lcb(root, C):
    path = [root]
    node = root
    while node.children:
        def score(c):
            if c.visits == 0:
                return -1.0
            q = c.total_reward / c.visits
            return q - C / math.sqrt(c.visits)
        node = max(node.children.values(), key=score)
        path.append(node)
    return path


def flat_hybrid_pick_new(entries, lookup_case, C):
    """entries: (iter, kind, script, old_score). Rescore with new weights."""
    rescored = []
    for it, kind, script, old_score in entries:
        new_score, is_match, found = relook(lookup_case, old_score)
        rescored.append((it, kind, script, new_score, is_match, found))

    freq_map = {}
    for it, kind, script, new_score, is_match, found in rescored:
        r = round(new_score, 4)
        freq_map[r] = freq_map.get(r, 0) + 1

    seen = {}
    for it, kind, script, new_score, is_match, found in rescored:
        key = script.strip()
        if key not in seen or new_score > seen[key][1]:
            seen[key] = (script, new_score, is_match)

    best_hybrid, best_score, best_match = -1e18, None, None
    for key, (script, new_score, is_match) in seen.items():
        r = round(new_score, 4)
        f = freq_map.get(r, 1)
        hybrid = new_score - C / math.sqrt(f)
        if hybrid > best_hybrid:
            best_hybrid = hybrid
            best_score = new_score
            best_match = is_match
    return best_score, best_match


# ---------------------------------------------------------------------------
# Per-case processing
# ---------------------------------------------------------------------------

def process_case(length, log_dir, case_num, lookup):
    d = log_dir_for_l1(case_num) if length == 1 else log_dir
    files = sorted(glob.glob(f"{d}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])
    lookup_case = lookup.get((str(length), str(case_num)))

    (root, iter_scripts, global_best_script, global_best_score, global_best_is_match,
     total_iters, node_meta, n_miss, n_tot) = parse_log_with_new_rewards(log_file, lookup_case)
    if root is None or total_iters == 0:
        return length, case_num, None

    out = {}
    out["BEST_SCORE"] = (global_best_score, global_best_is_match)

    for name, path_fn in [("OLD_total_reward", greedy_tr_path), ("Q_VALUE", greedy_q_path),
                           ("LCB_C=0.5", lambda rt: greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        is_match = node_meta.get(id(leaf))
        out[name] = (leaf.best, is_match)

    entries = extract_all_scored_scripts(log_file)
    hyb_score, hyb_match = flat_hybrid_pick_new(entries, lookup_case, 0.1) if entries else (None, None)
    out["HYBRID_C=0.1"] = (hyb_score, hyb_match)

    return length, case_num, (out, n_miss, n_tot)


def main():
    lookup = load_lookup()
    print(f"Loaded lookup covering {len(lookup)} cases, "
          f"{sum(len(v) for v in lookup.values())} unique-score entries")

    tasks = [(length, log_dir, c) for length, log_dir, n in CONFIGS for c in range(n)]
    results = {1: {}, 4: {}, 9: {}}
    miss_total = tot_total = 0

    for batch_start in range(0, len(tasks), 20):
        batch = tasks[batch_start:batch_start + 20]
        print(f"\n--- batch {batch_start}-{batch_start+len(batch)-1} ---", flush=True)
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, l, d, c, lookup): (l, c) for l, d, c in batch}
            for future in as_completed(futures):
                length, c = futures[future]
                try:
                    length_r, case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                if out is not None:
                    methods, n_miss, n_tot = out
                    results[length][case_num] = methods
                    miss_total += n_miss
                    tot_total += n_tot
                else:
                    results[length][case_num] = None
                print(f"L{length} c{case_num} done", flush=True)

    print(f"\nlookup miss rate: {miss_total}/{tot_total} ({100*miss_total/max(tot_total,1):.1f}%) "
          f"backprop events fell back to old score (no CSV entry)")

    print(f"\n{'='*70}\nResults with NEW weights "
          f"(fd_f1=0.1241, avg_col_score_1=0.2487, row_count_score=0.3562, max_missing_score=0.2710)\n{'='*70}")
    for length, log_dir, n in CONFIGS:
        cases = list(range(n))
        print(f"\nL{length}:")
        for name in METHOD_NAMES:
            n_ok = 0
            n_known = 0
            no_log = 0
            for c in cases:
                out = results[length].get(c)
                if out is None:
                    no_log += 1
                    continue
                score, is_match = out[name]
                if is_match is None:
                    continue  # unresolved (lookup miss on the winning entry) -- excluded from accuracy
                n_known += 1
                n_ok += bool(is_match)
            print(f"  {name:<18}: {n_ok}/{n_known} correct (of {n_known} resolvable; "
                  f"{no_log} no_log, {n - no_log - n_known} unresolved)")


if __name__ == "__main__":
    main()
