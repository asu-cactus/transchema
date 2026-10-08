"""
analyze_run14_c8_confidence_vs_correctness.py
===============================================
run14's L1 pilot case 8 is the one case still is_correct=False overall
(final: score=0.819, timeout_recovered). Extract EVERY script generated
during the search -- both simulate and critique-corrected, now BOTH carrying
a blended confidence (pipeline-frequency x self-report, see
_record_pipeline_confidence in Langraph/nodes.py) -- and run two-step
verification on each one:

  Step 1 (train): execute the script as-is, compare output to target.csv.
  Step 2 (test):  swap training_N.csv -> test_N.csv (+ output path ->
                   *_test_val.csv), execute, compare to the same target.csv.

Reports, per script: iteration, source (sim/critique), self-reported
confidence, blended confidence, det_score_value reward, train_correct,
test_correct -- then identifies the best-scored script (what the search
actually kept) vs. any test-correct scripts found and discarded along the
way, to explain why the final pick was wrong.

Usage: python3 analyze_run14_c8_confidence_vs_correctness.py
Run from: ~/transchema/
"""

import sys
import os
import re
import csv
import io
import subprocess
import tempfile
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, str(Path(__file__).parent))
from validation.hard_match import compare_tables_matching
import pandas as pd

LOG_DIR = Path("logs_langraph/rag_det_score_run14_l1_pilot20")
CASE_NUM = 8
SCRIPT_TIMEOUT = 90

RE_ITER_SELECT = re.compile(r"\[MCTS Select\] Iter (\d+):")
RE_QUERY_TYPE = re.compile(r"INFO - Query of Type : MCTS (\w+)")
RE_RESULT_RCV = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Result Recieved :")
RE_COST_LINE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Cost of the query")
RE_CODE_OPEN = re.compile(r"^```[Pp]ython\s*$")
RE_CODE_CLOSE = re.compile(r"^```\s*$")

# simulate's blended confidence rides along in execute_and_score's components dict
RE_EXEC_SCORE = re.compile(
    r"\[execute_and_score\] Iter (\d+): reward=([\d.]+).*?confidence=([^,}]+)"
)
# critique's line: confidence='<raw self-reported>' (<blended>)
RE_CRIT_LINE = re.compile(
    r"\[mcts_critique\] Iter (\d+): score ([\d.]+) → ([\d.]+), confidence='([^']*)' \(([^)]+)\)"
)


def _extract_last_code_block(lines):
    blocks = []
    in_block = False
    buf = []
    for line in lines:
        stripped = line.rstrip()
        if RE_CODE_OPEN.match(stripped):
            in_block = True
            buf = []
        elif RE_CODE_CLOSE.match(stripped) and in_block:
            in_block = False
            content = "\n".join(buf).strip()
            if content and "<corrected code here>" not in content:
                blocks.append(content)
        elif in_block:
            buf.append(line)
    return blocks[-1] if blocks else None


def parse_case_log(log_path: Path):
    """Returns list of dicts: {iter, source, script, self_reported, blended, reward}."""
    text = log_path.read_text(errors="replace")
    lines = text.splitlines()

    entries = []
    cur_iter = -1
    current_query_type = None
    in_response = False
    response_lines = []

    iter_sim_conf = {}    # iter -> (blended,)  from execute_and_score right after a Simulate call
    iter_crit_conf = {}   # iter -> (self_reported_raw, blended, reward_after)

    for line in lines:
        m = RE_ITER_SELECT.search(line)
        if m:
            cur_iter = int(m.group(1))

        m = RE_EXEC_SCORE.search(line)
        if m:
            it, reward, conf = m.group(1), m.group(2), m.group(3).strip()
            iter_sim_conf[int(it)] = (
                float(reward), None if conf == "None" else float(conf)
            )

        m = RE_CRIT_LINE.search(line)
        if m:
            it, before, after, raw, blended = m.groups()
            iter_crit_conf[int(it)] = (raw, None if blended == "None" else float(blended), float(after))

        m = RE_QUERY_TYPE.search(line)
        if m:
            current_query_type = m.group(1)
            in_response = False
            response_lines = []
            continue

        if RE_RESULT_RCV.search(line):
            in_response = True
            response_lines = [line]
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

    for e in entries:
        if e["source"] == "simulate":
            reward, blended = iter_sim_conf.get(e["iter"], (None, None))
            e["self_reported"] = None
            e["blended"] = blended
            e["reward"] = reward
        else:
            raw, blended, reward = iter_crit_conf.get(e["iter"], ("", None, None))
            e["self_reported"] = raw
            e["blended"] = blended
            e["reward"] = reward

    return entries


def swap_training_to_test(script: str) -> str:
    swapped = re.sub(r"training_(\d+)\.csv", r"test_\1.csv", script)
    swapped = re.sub(r"(target_multisource[^.]*?)\.csv", r"\1_test_val.csv", swapped)
    return swapped


def run_script(script: str, work_dir: Path):
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="analyze_conf_")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            f.write(script)
        result = subprocess.run(
            [sys.executable, tmp_path], cwd=str(work_dir),
            capture_output=True, text=True, timeout=SCRIPT_TIMEOUT,
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout)[:300]
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)[:200]
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def validate(output_path: Path, gt_path: Path):
    if not output_path.exists() or not gt_path.exists():
        return False, 0.0
    try:
        df_output = pd.read_csv(output_path, low_memory=False)
        df_gt = pd.read_csv(gt_path, low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            avg_sim, is_match, _, _ = compare_tables_matching(df_output, df_gt)
        return bool(is_match), float(avg_sim)
    except Exception:
        return False, 0.0


def two_step_verify(script: str, case_num: int, work_dir: Path):
    case_dir = work_dir / f"autopipeline-benchmarks/github-pipelines/length1_{case_num}"
    gt_path = case_dir / "target.csv"

    train_ok, train_err = run_script(script, work_dir)
    m = re.search(r'to_csv\(\s*["\']([^"\']*target_multisource[^"\']*\.csv)["\']', script)
    train_out = work_dir / m.group(1) if m else None
    train_correct, train_sim = (False, 0.0)
    if train_ok and train_out is not None:
        train_correct, train_sim = validate(train_out, gt_path)

    test_script = swap_training_to_test(script)
    test_ok, test_err = run_script(test_script, work_dir)
    test_out = work_dir / swap_training_to_test(m.group(1)) if m else None
    test_correct, test_sim = (False, 0.0)
    if test_ok and test_out is not None:
        test_correct, test_sim = validate(test_out, gt_path)

    return {
        "train_ok": train_ok, "train_correct": train_correct, "train_sim": round(train_sim, 4),
        "test_ok": test_ok, "test_correct": test_correct, "test_sim": round(test_sim, 4),
    }


def main():
    work_dir = Path(".").resolve()
    log_files = sorted((LOG_DIR / f"cases_c{CASE_NUM}").glob("*.log"))
    log_path = log_files[-1]  # latest timestamp = the completed (non-killed) run
    entries = parse_case_log(log_path)
    print(f"=== Case {CASE_NUM}: {len(entries)} scripts extracted ({log_path.name}) ===\n")

    all_rows = []
    for e in entries:
        res = two_step_verify(e["script"], CASE_NUM, work_dir)
        row = {"iter": e["iter"], "source": e["source"], "self_reported": e["self_reported"],
               "blended": e["blended"], "reward": e["reward"], **res}
        all_rows.append(row)
        tag = lambda ok, correct: "correct" if (ok and correct) else ("wrong" if ok else "ERR")
        sr = e["self_reported"] if e["self_reported"] is not None else "  - "
        bl = f"{e['blended']:.3f}" if e["blended"] is not None else "  -  "
        rw = f"{e['reward']:.4f}" if e["reward"] is not None else "  -   "
        print(
            f"  iter={e['iter']:3d} {e['source']:9s} reward={rw} self_reported={sr!s:6s} blended={bl}  "
            f"train={tag(res['train_ok'], res['train_correct']):7s} test={tag(res['test_ok'], res['test_correct'])}"
        )

    print(f"\n{'='*78}")
    best = max(all_rows, key=lambda r: r["reward"] if r["reward"] is not None else -1)
    print(f"BEST-SCORED script: iter={best['iter']} source={best['source']} reward={best['reward']:.4f} "
          f"blended_confidence={best['blended']} -> test_correct={best['test_correct']}")

    test_correct_rows = [r for r in all_rows if r["test_correct"]]
    print(f"\n{len(test_correct_rows)}/{len(all_rows)} scripts were test_correct. Their rewards:")
    for r in sorted(test_correct_rows, key=lambda r: -(r["reward"] or 0)):
        print(f"  iter={r['iter']:3d} {r['source']:9s} reward={r['reward']:.4f} blended_confidence={r['blended']}")

    if test_correct_rows:
        best_correct = max(test_correct_rows, key=lambda r: r["reward"])
        print(f"\nBest test_correct candidate: iter={best_correct['iter']} reward={best_correct['reward']:.4f} "
              f"vs. selected best reward={best['reward']:.4f} "
              f"(gap={best['reward'] - best_correct['reward']:+.4f})")

    out_path = Path("analyze_run14_c8_confidence_vs_correctness_results.csv")
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nDetailed results -> {out_path}")


if __name__ == "__main__":
    main()
