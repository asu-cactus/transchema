"""
analyze_run15_hybrid_freq_adjusted.py
=======================================
Re-does the "frequency adjusted score" counterfactual for run15's 100 L1
cases using the ACTUAL prior methodology from fit_hybrid_weights_lp.py
(previously used, per user, to get good results), not a reinvented one:

    hybrid_i = w.x_i - C_HYBRID / sqrt(freq_i)

  x_i      = [fd_f1, avg_col_score_1, row_count_score, max_missing_score]
             for candidate i (the 4 structural components already logged,
             confidence excluded entirely).
  w        = the CURRENT L1 structural weights [.285, .288, .266, .161]
             (not confidence, and not re-fit here -- using what's already
             established for this length).
  freq_i   = count of ALL scored events in the case's log (every iteration,
             both simulate and critique, NOT deduplicated by script identity)
             whose own structural score rounds (4 decimals) to the SAME
             value as candidate i's score -- a penalty for scores that keep
             recurring, computed once per case over the full log before any
             selection happens (matches fit_hybrid_weights_lp.py's
             build_case_data/eval_fixed_freq_accuracy: freq_map keyed by
             rounded score, NOT by pipeline/script identity).
  C_HYBRID = 0.1 (the "hybrid c=0.1" constant from fit_hybrid_weights_lp.py).

Per case: selects argmax_i hybrid_i over ALL scored candidates (a global
argmax over the whole case's log, matching eval_fixed_freq_accuracy's
one-shot selection -- not a running "best so far" replay), then two-step-
verifies (TEST side) whichever script wins. Reports accuracy vs. run15's
actual 84/100 and the earlier (wrong) no-confidence-only replay (76.5%).

Runs 25 cases in parallel (ProcessPoolExecutor) -- no LLM calls.

Usage: python3 analyze_run15_hybrid_freq_adjusted.py [--cases N] [--workers 25]
Run from: ~/transchema/
"""

import sys
import os
import re
import csv
import io
import math
import argparse
import subprocess
import tempfile
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))

LOG_DIR = Path("logs_langraph/rag_det_score_run15_l1_full100")
SCRIPT_TIMEOUT = 90
C_HYBRID = 0.1

# Current L1 structural weights (no confidence) -- same as
# analyze_run15_confidence_counterfactuals.py's ORIG_STRUCT_WEIGHTS.
STRUCT_WEIGHTS = {"fd_f1": 0.285, "avg_col_score_1": 0.288, "row_count_score": 0.266, "max_missing_score": 0.161}

# ── Log parsing regexes (same as analyze_run15_confidence_counterfactuals.py) ─
RE_ITER_SELECT = re.compile(r"\[MCTS Select\] Iter (\d+):")
RE_QUERY_TYPE = re.compile(r"INFO - Query of Type : MCTS (\w+)")
RE_RESULT_RCV = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Result Recieved :")
RE_COST_LINE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Cost of the query")
RE_CODE_OPEN = re.compile(r"^```[Pp]ython\s*$")
RE_CODE_CLOSE = re.compile(r"^```\s*$")

_COMP_RE = r"fd_f1=([\d.]+), avg_col_score_1=([^,]+), row_count_score=([\d.]+), max_missing_score=([\d.]+)"
RE_EXEC_SCORE = re.compile(r"\[execute_and_score\] Iter (\d+): reward=[\d.]+.*?components=\{" + _COMP_RE)
RE_CRIT_SCORE = re.compile(r"\[mcts_critique\] Iter (\d+): score [\d.]+ → [\d.]+, confidence='[^']*' \([^)]+\), components=\{" + _COMP_RE)


def _extract_last_code_block(lines):
    blocks, in_block, buf = [], False, []
    for line in lines:
        stripped = line.rstrip()
        if RE_CODE_OPEN.match(stripped):
            in_block, buf = True, []
        elif RE_CODE_CLOSE.match(stripped) and in_block:
            in_block = False
            content = "\n".join(buf).strip()
            if content and "<corrected code here>" not in content:
                blocks.append(content)
        elif in_block:
            buf.append(line)
    return blocks[-1] if blocks else None


def parse_case_log(log_path: Path):
    """Returns chronological list of ALL scored events (not deduplicated):
    {iter, source, script, components}."""
    text = log_path.read_text(errors="replace")
    lines = text.splitlines()

    entries = []
    cur_iter = -1
    current_query_type = None
    in_response = False
    response_lines = []
    iter_comp = {}

    for line in lines:
        m = RE_ITER_SELECT.search(line)
        if m:
            cur_iter = int(m.group(1))

        m = RE_EXEC_SCORE.search(line)
        if m:
            it, fd, col, row, miss = m.groups()
            col_val = None if col.strip() == "None" else float(col)
            iter_comp.setdefault(int(it), {})["simulate"] = {
                "fd_f1": float(fd), "avg_col_score_1": col_val,
                "row_count_score": float(row), "max_missing_score": float(miss),
            }
        m = RE_CRIT_SCORE.search(line)
        if m:
            it, fd, col, row, miss = m.groups()
            col_val = None if col.strip() == "None" else float(col)
            iter_comp.setdefault(int(it), {})["critique"] = {
                "fd_f1": float(fd), "avg_col_score_1": col_val,
                "row_count_score": float(row), "max_missing_score": float(miss),
            }

        m = RE_QUERY_TYPE.search(line)
        if m:
            current_query_type = m.group(1)
            in_response, response_lines = False, []
            continue
        if RE_RESULT_RCV.search(line):
            in_response, response_lines = True, [line]
            continue
        if RE_COST_LINE.search(line) and in_response:
            in_response = False
            code = _extract_last_code_block(response_lines)
            if code and current_query_type in ("Simulate", "Critique") and cur_iter >= 0:
                entries.append({"iter": cur_iter, "source": current_query_type.lower(), "script": code})
            response_lines = []
            continue
        if in_response:
            response_lines.append(line)

    out = []
    for e in entries:
        comp = iter_comp.get(e["iter"], {}).get(e["source"])
        if not comp or comp.get("avg_col_score_1") is None:
            continue
        out.append({**e, "components": comp})
    return out


def weighted_score(components: dict, weights: dict) -> float:
    avail = {k: v for k, v in components.items() if v is not None}
    w = {k: weights.get(k, 0.0) for k in avail}
    w_sum = sum(w.values()) or 1.0
    return sum(w[k] * avail[k] for k in avail) / w_sum


def swap_training_to_test(script: str) -> str:
    swapped = re.sub(r"training_(\d+)\.csv", r"test_\1.csv", script)
    swapped = re.sub(r"(target_multisource[^.]*?)\.csv", r"\1_test_val.csv", swapped)
    return swapped


def run_script(script: str, work_dir: Path) -> bool:
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="hf_")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            f.write(script)
        result = subprocess.run([sys.executable, tmp_path], cwd=str(work_dir),
                                 capture_output=True, text=True, timeout=SCRIPT_TIMEOUT)
        return result.returncode == 0
    except Exception:
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def test_correct(script: str, case_num: int, work_dir: Path) -> bool:
    from validation.hard_match import compare_tables_matching
    import pandas as pd

    case_dir = work_dir / f"autopipeline-benchmarks/github-pipelines/length1_{case_num}"
    gt_path = case_dir / "target.csv"
    m = re.search(r'to_csv\(\s*["\']([^"\']*target_multisource[^"\']*\.csv)["\']', script)
    if not m or not gt_path.exists():
        return False
    if not run_script(swap_training_to_test(script), work_dir):
        return False
    out_path = work_dir / swap_training_to_test(m.group(1))
    if not out_path.exists():
        return False
    try:
        df_output = pd.read_csv(out_path, low_memory=False)
        df_gt = pd.read_csv(gt_path, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            _, is_match, _, _ = compare_tables_matching(df_output, df_gt)
        return bool(is_match)
    except Exception:
        return False


def process_case(case_num: int):
    work_dir = Path(".").resolve()
    log_files = sorted((LOG_DIR / f"cases_c{case_num}").glob("*.log"))
    if not log_files:
        return {"case": case_num, "n_candidates": 0, "score": None, "freq": None, "correct": None, "skipped": True}

    entries = parse_case_log(log_files[-1])
    if not entries:
        return {"case": case_num, "n_candidates": 0, "score": None, "freq": None, "correct": None, "skipped": True}

    # Score every event (structural-only, no confidence).
    for e in entries:
        e["score"] = weighted_score(e["components"], STRUCT_WEIGHTS)

    # freq_map: count ALL raw events (not deduplicated) by rounded score.
    freq_map = {}
    for e in entries:
        s = round(e["score"], 4)
        freq_map[s] = freq_map.get(s, 0) + 1

    # Global argmax of hybrid_i = score_i - C/sqrt(freq_i) over all events.
    def hybrid(e):
        freq = freq_map[round(e["score"], 4)]
        return e["score"] - C_HYBRID / math.sqrt(freq)

    best = max(entries, key=hybrid)
    best_freq = freq_map[round(best["score"], 4)]

    correct = test_correct(best["script"], case_num, work_dir)
    return {"case": case_num, "n_candidates": len(entries), "score": round(best["score"], 4),
            "freq": best_freq, "correct": correct, "skipped": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=int, default=100)
    ap.add_argument("--workers", type=int, default=25)
    args = ap.parse_args()

    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(process_case, c): c for c in range(args.cases)}
        for fut in as_completed(futures):
            r = fut.result()
            rows.append(r)
            if r["skipped"]:
                print(f"c{r['case']:3d}: no scoreable candidates found, skipping")
            else:
                print(f"c{r['case']:3d}  n={r['n_candidates']:3d}  score={r['score']:.4f}  freq={r['freq']:3d}  correct={r['correct']}")

    rows.sort(key=lambda r: r["case"])
    scored = [r for r in rows if not r["skipped"]]
    correct_n = sum(1 for r in scored if r["correct"])
    n = len(scored)
    print(f"\n{'='*70}")
    print(f"Hybrid frequency-adjusted (hybrid_i = w.x_i - {C_HYBRID}/sqrt(freq_i)) accuracy")
    print(f"{'='*70}")
    print(f"  {correct_n}/{n} ({correct_n/n:.1%})" if n else "  no cases scored")
    print(f"  vs. run15 actual (max-score w/ 25% confidence blend): 84/100 (84.0%)")
    print(f"  vs. naive no-confidence (plain argmax, no freq penalty): 75/98 (76.5%)")

    out_path = Path("analyze_run15_hybrid_freq_adjusted_results.csv")
    if rows:
        with out_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\nDetailed results -> {out_path}")


if __name__ == "__main__":
    main()
