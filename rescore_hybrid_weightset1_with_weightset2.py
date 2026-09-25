"""
rescore_hybrid_weightset1_with_weightset2.py
===========================
weight-set-1's live run (run_score_weights_60cases.sh, tag=weightset1) used
weight-set-1 for BOTH the MCTS reward (drives search/tree) and HYBRID_C's
score(i) term. This script asks: on that SAME already-completed run (same
search trajectory, same tree, same freq counts -- nothing is re-run), what
if HYBRID_C's score(i) term used weight-set-2 instead?

freq stays exactly as it was during the live search (computed from the
weight-set-1 scores that actually drove exploration -- a fixed historical
fact, same principle established earlier in this session: changing which
weights score a script doesn't change how many times the search actually
produced that score). Only score(i) is recomputed, using the 4 raw
(unweighted) components every log line now carries
(components={fd_f1=.., avg_col_score_1=.., row_count_score=.., max_missing_score=..}),
so no re-execution of MCTS/scoring is needed -- purely a log-parsing exercise.

hybrid(i) = (w2 . components_i) - 0.1/sqrt(freq[round(old_score_i, 4)])

The winning script per case is then REAL-executed against test data
(run_and_check) to get a genuine accuracy number, comparable to weight-set-1's
native HYBRID_C=0.1 result (39/60) already computed by
analyze_score_weights_60cases_all_methods.py.

Usage: python3 rescore_hybrid_weightset1_with_weightset2.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import re
import glob
import math
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from eval_run8_training import (
    RE_QUERY_TYPE, RE_RESULT_RCV, RE_COST_LINE, RE_SELECT, RE_SCORE,
    RE_CRIT_SCORE, RE_BP_DONE, _extract_last_code_block,
)
from analyze_run8_failed_case_scripts import run_and_check
from analyze_score_weights_60cases_all_methods import CASES_BY_LENGTH

RE_COMPONENTS = re.compile(r"components=\{([^}]*)\}")

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]
W2 = {  # weight-set-2: frequency-aware pairwise logistic regression fit
    "fd_f1": 0.14533279963769782,
    "avg_col_score_1": 0.2297057602581925,
    "row_count_score": 0.583980950520166,
    "max_missing_score": 0.09575390137409956,
}
C_HYBRID = 0.1


def _parse_components(line: str) -> Optional[Dict[str, float]]:
    m = RE_COMPONENTS.search(line)
    if not m:
        return None
    out = {}
    for kv in m.group(1).split(", "):
        k, v = kv.split("=", 1)
        try:
            out[k] = float(v)
        except ValueError:
            return None
    return out


def extract_all_scored_scripts_with_components(filepath: Path) -> List[Tuple[int, str, str, float, Optional[Dict[str, float]]]]:
    """Same walk as analyze_run8_failed_case_scripts.extract_all_scored_scripts,
    plus each event's parsed `components={...}` dict from the same log line."""
    text = filepath.read_text(errors="replace")
    lines = text.splitlines()

    cur_iter = -1
    pre_score = 0.0
    crit_score = 0.0
    pre_components: Optional[Dict[str, float]] = None
    crit_components: Optional[Dict[str, float]] = None
    pending_sim: Optional[str] = None
    pending_crit: Optional[str] = None

    current_query_type: Optional[str] = None
    in_llm_response = False
    response_lines: List[str] = []

    out: List[Tuple[int, str, str, float, Optional[Dict[str, float]]]] = []

    def flush_iter():
        nonlocal pending_sim, pending_crit
        if pending_sim is not None:
            out.append((cur_iter, "sim", pending_sim, pre_score, pre_components))
        if pending_crit is not None:
            out.append((cur_iter, "critique", pending_crit, crit_score, crit_components))
        pending_sim = None
        pending_crit = None

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
                if current_query_type == "Simulate":
                    pending_sim = code
                elif current_query_type == "Critique":
                    pending_crit = code
            response_lines = []
        elif in_llm_response:
            response_lines.append(line)

        m = RE_SELECT.search(line)
        if m:
            cur_iter = int(m.group(1))
            pre_score = 0.0
            crit_score = 0.0
            pre_components = None
            crit_components = None

        m = RE_SCORE.search(line)
        if m and int(m.group(1)) == cur_iter:
            pre_score = float(m.group(2))
            pre_components = _parse_components(line)

        m = RE_CRIT_SCORE.search(line)
        if m and int(m.group(1)) == cur_iter:
            crit_score = float(m.group(2))
            crit_components = _parse_components(line)

        m = RE_BP_DONE.search(line)
        if m and int(m.group(1)) == cur_iter:
            flush_iter()

    return out


def rescored_hybrid_pick(entries, w2, C):
    """freq bucketed on the OLD (weight-set-1) score -- a fixed historical
    fact of what the live search actually produced -- while score(i) is
    recomputed from each event's logged raw components under w2."""
    freq_map = {}
    for it, kind, script, old_score, components in entries:
        r = round(old_score, 4)
        freq_map[r] = freq_map.get(r, 0) + 1

    seen = {}
    for it, kind, script, old_score, components in entries:
        key = script.strip()
        if key not in seen or old_score > seen[key][1]:
            seen[key] = (script, old_score, components)

    best_hybrid, best_script, best_new_score = -1e18, None, None
    for key, (script, old_score, components) in seen.items():
        if components:
            new_score = sum(w2[f] * components[f] for f in FEATURES)
        else:
            new_score = old_score  # fallback: no components logged for this event
        f = freq_map.get(round(old_score, 4), 1)
        hybrid = new_score - C / math.sqrt(f)
        if hybrid > best_hybrid:
            best_hybrid = hybrid
            best_script = script
            best_new_score = new_score
    return best_script, best_new_score


def process_case(case_num: int, log_dir: str, length: int):
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])
    entries = extract_all_scored_scripts_with_components(log_file)
    if not entries:
        return case_num, None

    script, new_score = rescored_hybrid_pick(entries, W2, C_HYBRID)
    ok, note = run_and_check(script, case_num, length=length) if script else (False, "no_script")
    return case_num, (new_score, ok)


def main():
    results_by_length = {}
    for length, cases in CASES_BY_LENGTH.items():
        log_dir = f"logs_langraph/score_weights_60cases_weightset1_l{length}"
        print(f"\n--- L{length}: {len(cases)} cases ---", flush=True)
        results = {}
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, c, log_dir, length): c for c in cases}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"L{length} c{case_num}: {out}", flush=True)
        results_by_length[length] = results

    print(f"\n{'='*70}\nHYBRID_C=0.1 rescored with weight-set-2's weights\n"
          f"(on weight-set-1's live run: same search/tree/freq, only score(i) changes)\n{'='*70}")
    combined_ok = combined_n = 0
    for length, cases in CASES_BY_LENGTH.items():
        results = results_by_length[length]
        n = len([c for c in results if results[c] is not None])
        n_ok = sum(1 for c, out in results.items() if out is not None and out[1])
        wrong = sorted(c for c, out in results.items() if out is not None and not out[1])
        print(f"  L{length}: {n_ok}/{n} correct   wrong={wrong}")
        combined_ok += n_ok
        combined_n += n
    print(f"\n  COMBINED: {combined_ok}/{combined_n} ({100*combined_ok/max(combined_n,1):.1f}%)")
    print("\n  (compare to weight-set-1's NATIVE HYBRID_C=0.1: 39/60 = 65.0%)")


if __name__ == "__main__":
    main()
