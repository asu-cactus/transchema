"""
analyze_run8_failed_case_scripts.py
====================================
For a set of run8 L1 cases where Method A (global-best-training-score script)
was WRONG on test data, but run7 got them right: extract every unique script
seen anywhere in the run8 MCTS log (sim + critique, across all iterations),
run each one on TEST data, and check correctness.

For each case, reports:
  - The CHOSEN script (Method A / global best training score) and its score.
  - Whether a CORRECT script exists anywhere in the log.
  - If so, its training score, and how many scripts scored higher than it
    (i.e. how badly the scoring function ranked it) or explicitly whether the
    correct script was never found at all (recovery/regeneration issue).

Usage: python3 analyze_run8_failed_case_scripts.py [case_id ...]
Run from: ~/transchema/  (needs `source env/bin/activate` first)
"""
import sys
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, ".")

from eval_run8_training import (
    RE_QUERY_TYPE, RE_RESULT_RCV, RE_COST_LINE, RE_SELECT, RE_SCORE,
    RE_CRIT_SCORE, RE_BP_DONE, _extract_last_code_block,
    swap_training_to_test, run_script, validate_output,
)

LOG_DIR  = "logs_langraph/rag_det_score_run8_l1_training"
WORK_DIR = Path(".").resolve()

DEFAULT_CASES = [13, 14, 25, 33, 43, 45, 63, 65, 73, 79]


def extract_all_scored_scripts(filepath: Path) -> List[Tuple[int, str, str, float]]:
    """
    Walk the log and return every (iter, kind, script, score) seen, where
    kind is "sim" or "critique". Score is the reward attributed to that
    iteration's sim/critique step (0.0 if never scored, e.g. failed exec).
    """
    text = filepath.read_text(errors="replace")
    lines = text.splitlines()

    cur_iter = -1
    pre_score = 0.0
    crit_score = 0.0
    pending_sim: Optional[str] = None
    pending_crit: Optional[str] = None

    current_query_type: Optional[str] = None
    in_llm_response = False
    response_lines: List[str] = []

    out: List[Tuple[int, str, str, float]] = []

    def flush_iter():
        nonlocal pending_sim, pending_crit
        if pending_sim is not None:
            out.append((cur_iter, "sim", pending_sim, pre_score))
        if pending_crit is not None:
            out.append((cur_iter, "critique", pending_crit, crit_score))
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
            # New iteration starting — flush anything left over defensively
            # (should already have been flushed at RE_BP_DONE of prior iter).
            cur_iter = int(m.group(1))
            pre_score = 0.0
            crit_score = 0.0

        m = RE_SCORE.search(line)
        if m and int(m.group(1)) == cur_iter:
            pre_score = float(m.group(2))

        m = RE_CRIT_SCORE.search(line)
        if m and int(m.group(1)) == cur_iter:
            crit_score = float(m.group(2))

        m = RE_BP_DONE.search(line)
        if m and int(m.group(1)) == cur_iter:
            flush_iter()

    return out


def run_and_check(script: str, case_num: int) -> Tuple[bool, str]:
    test_script = swap_training_to_test(script)
    ok, err = run_script(test_script, WORK_DIR)
    if not ok:
        return False, f"run_failed: {err[:80]}"
    correct, sim = validate_output(case_num, WORK_DIR)
    return correct, f"sim={sim:.3f}"


def analyze_case(case_num: int) -> None:
    log_files = sorted(glob.glob(f"{LOG_DIR}/cases_c{case_num}/*.log"))
    print(f"\n{'='*90}\nCase {case_num}\n{'='*90}")
    if not log_files:
        print("  No log file found.")
        return
    log_file = Path(log_files[0])

    entries = extract_all_scored_scripts(log_file)
    if not entries:
        print("  No scripts extracted from log.")
        return

    # The CHOSEN script (Method A): highest score among sim entries, matching
    # eval_run8_training.py's global_best logic (sim OR critique, whichever
    # highest, ties favouring later occurrence is irrelevant here).
    chosen_iter, chosen_kind, chosen_script, chosen_score = max(
        entries, key=lambda e: e[3]
    )
    print(f"  Extracted {len(entries)} scored script instances "
          f"({len(set(e[2] for e in entries))} unique scripts)")
    print(f"  CHOSEN (Method A, highest training score): "
          f"iter={chosen_iter} kind={chosen_kind} score={chosen_score:.4f}")

    chosen_score_occurrences = sum(1 for _, _, _, sc in entries if sc == chosen_score)

    chosen_correct, chosen_note = run_and_check(chosen_script, case_num)
    chosen_label = "correct" if chosen_correct else "wrong"
    print(f"    -> test result: {'CORRECT' if chosen_correct else 'WRONG'} ({chosen_note})")
    print(f"    -> this {chosen_label} score ({chosen_score:.4f}) appeared "
          f"{chosen_score_occurrences}/{len(entries)} times in the log")
    print(f"  ---- CHOSEN script ----\n{chosen_script}\n  ------------------------")

    # Dedupe remaining unique scripts (by text), evaluate each on test data.
    seen: Dict[str, Tuple[int, str, float]] = {}
    for it, kind, script, score in entries:
        key = script.strip()
        if key not in seen or score > seen[key][2]:
            seen[key] = (it, kind, score)

    results = []
    for script, (it, kind, score) in seen.items():
        correct, note = run_and_check(script, case_num)
        results.append((script, it, kind, score, correct, note))

    correct_scripts = [r for r in results if r[4]]
    if not correct_scripts:
        print("  No correct script found ANYWHERE in the log — MCTS never "
              "generated a correct pipeline for this case (not a scoring bug).")
        return

    # Best (highest-scoring) correct script
    best_correct = max(correct_scripts, key=lambda r: r[3])
    n_scored_higher = sum(1 for r in results if r[3] > best_correct[3])
    best_correct_score_occurrences = sum(1 for _, _, _, sc in entries if sc == best_correct[3])

    # Total instances (across all unique scripts) that were correct vs wrong,
    # weighted by how many times each unique script recurred in the log.
    correct_keys = {r[0].strip() for r in correct_scripts}
    right_occurrences = sum(1 for _, _, s, _ in entries if s.strip() in correct_keys)
    wrong_occurrences = len(entries) - right_occurrences

    print(f"  {len(correct_scripts)} correct script(s) found among "
          f"{len(results)} unique scripts.")
    print(f"  Across all {len(entries)} scored instances in the log: "
          f"{right_occurrences} came from a correct script, "
          f"{wrong_occurrences} came from a wrong script.")
    print(f"  BEST correct script: iter={best_correct[1]} kind={best_correct[2]} "
          f"score={best_correct[3]:.4f}")
    print(f"    -> {n_scored_higher} other (incorrect) script(s) scored HIGHER "
          f"than this correct one.")
    print(f"    -> this correct score ({best_correct[3]:.4f}) appeared "
          f"{best_correct_score_occurrences}/{len(entries)} times in the log")
    print(f"  ---- BEST CORRECT script ----\n{best_correct[0]}\n  ------------------------")
    if chosen_correct:
        print("  (Chosen script was already correct — should not be in the "
              "failure list; check upstream eval.)")
    else:
        gap = chosen_score - best_correct[3]
        print(f"  Score gap: chosen(wrong)={chosen_score:.4f} vs "
              f"best_correct={best_correct[3]:.4f}  (Δ={gap:+.4f})")


def main():
    cases = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else DEFAULT_CASES
    for c in cases:
        analyze_case(c)


if __name__ == "__main__":
    main()
