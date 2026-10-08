"""
analyze_run13_confidence_vs_correctness_c4_c8.py
=================================================
For run13's L1 pilot cases 4 and 8 (both ended is_correct=False overall),
extract EVERY script generated during the search -- both plain simulation
scripts (no confidence) and critique-corrected scripts (with the parsed
$CONFIDENCE$ value) -- and run two-step verification on each one:

  Step 1 (train): execute the script as-is, compare output to target.csv.
  Step 2 (test):  swap training_N.csv -> test_N.csv (+ output path ->
                   *_test_val.csv), execute, compare to the same target.csv.
                   (Mirrors util.utils.make_test_validation_script, the same
                   swap the live MCTS timeout-recovery path uses.)

Reports, per script: iteration, source (sim/critique), confidence (None for
sim), train_correct, test_correct. Then buckets critique-script confidence
values by correct vs incorrect outcome.

Usage: python3 analyze_run13_confidence_vs_correctness_c4_c8.py
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

LOG_DIR = Path("logs_langraph/rag_det_score_run13_l1_pilot20")
CASES = [4, 8]
SCRIPT_TIMEOUT = 90

RE_ITER_SELECT = re.compile(r"\[MCTS Select\] Iter (\d+):")
RE_QUERY_TYPE = re.compile(r"INFO - Query of Type : MCTS (\w+)")
RE_RESULT_RCV = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Result Recieved :")
RE_COST_LINE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Cost of the query")
RE_CODE_OPEN = re.compile(r"^```[Pp]ython\s*$")
RE_CODE_CLOSE = re.compile(r"^```\s*$")
RE_CRIT_CONF = re.compile(
    r"\[mcts_critique\] Iter (\d+): score [\d.]+ → [\d.]+, confidence='([^']*)' \(([^)]+)\)"
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
    """Returns list of dicts: {iter, source, script, confidence_raw, confidence}."""
    text = log_path.read_text(errors="replace")
    lines = text.splitlines()

    entries = []
    cur_iter = -1
    current_query_type = None
    in_response = False
    response_lines = []

    # iter -> confidence (raw, float|None), filled from RE_CRIT_CONF as we go
    iter_confidence = {}

    for line in lines:
        m = RE_ITER_SELECT.search(line)
        if m:
            cur_iter = int(m.group(1))

        m = RE_CRIT_CONF.search(line)
        if m:
            it, raw, numeric = m.group(1), m.group(2), m.group(3)
            conf = None if numeric == "None" else float(numeric)
            iter_confidence[int(it)] = (raw, conf)

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
                entries.append(
                    {
                        "iter": cur_iter,
                        "source": current_query_type.lower(),
                        "script": code,
                    }
                )
            response_lines = []
            continue

        if in_response:
            response_lines.append(line)

    # attach confidence to critique entries (recorded slightly after code block
    # in log order, so do it as a second pass)
    for e in entries:
        if e["source"] == "critique":
            raw, conf = iter_confidence.get(e["iter"], ("", None))
            e["confidence_raw"] = raw
            e["confidence"] = conf
        else:
            e["confidence_raw"] = ""
            e["confidence"] = None

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
            [sys.executable, tmp_path],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT,
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

    # Step 1: train (script as-is; output path is whatever the script wrote)
    train_ok, train_err = run_script(script, work_dir)
    # locate output path the script itself writes to (target_multisource*.csv, not _test_val)
    m = re.search(r'to_csv\(\s*["\']([^"\']*target_multisource[^"\']*\.csv)["\']', script)
    train_out = work_dir / m.group(1) if m else None
    train_correct, train_sim = (False, 0.0)
    if train_ok and train_out is not None:
        train_correct, train_sim = validate(train_out, gt_path)

    # Step 2: test (swap paths, execute, compare _test_val output)
    test_script = swap_training_to_test(script)
    test_ok, test_err = run_script(test_script, work_dir)
    test_out = None
    if m:
        swapped_rel = swap_training_to_test(m.group(1))
        test_out = work_dir / swapped_rel
    test_correct, test_sim = (False, 0.0)
    if test_ok and test_out is not None:
        test_correct, test_sim = validate(test_out, gt_path)

    return {
        "train_ok": train_ok, "train_correct": train_correct, "train_sim": round(train_sim, 4),
        "train_err": train_err[:120] if not train_ok else "",
        "test_ok": test_ok, "test_correct": test_correct, "test_sim": round(test_sim, 4),
        "test_err": test_err[:120] if not test_ok else "",
    }


def main():
    work_dir = Path(".").resolve()
    all_rows = []

    for case_num in CASES:
        log_files = sorted((LOG_DIR / f"cases_c{case_num}").glob("*.log"))
        if not log_files:
            print(f"c{case_num}: no log file found, skipping")
            continue
        log_path = log_files[0]
        entries = parse_case_log(log_path)
        print(f"\n=== Case {case_num}: {len(entries)} scripts extracted ({log_path.name}) ===")

        for e in entries:
            res = two_step_verify(e["script"], case_num, work_dir)
            row = {
                "case": case_num,
                "iter": e["iter"],
                "source": e["source"],
                "confidence": e["confidence"],
                **res,
            }
            all_rows.append(row)
            tag = lambda ok, correct: "✓" if (ok and correct) else ("✗" if ok else "ERR")
            conf_str = f"{e['confidence']:.2f}" if e["confidence"] is not None else " N/A"
            print(
                f"  iter={e['iter']:3d} {e['source']:9s} conf={conf_str}  "
                f"train={tag(res['train_ok'], res['train_correct'])}  "
                f"test={tag(res['test_ok'], res['test_correct'])}"
            )

    # ── Confidence vs correctness rollup (critique scripts only) ───────────
    crit_rows = [r for r in all_rows if r["source"] == "critique" and r["confidence"] is not None]
    print(f"\n{'='*70}")
    print("Critique-script confidence vs correctness (train OR test correct = 'correct')")
    print(f"{'='*70}")
    correct_confs = [r["confidence"] for r in crit_rows if r["train_correct"] or r["test_correct"]]
    incorrect_confs = [r["confidence"] for r in crit_rows if not (r["train_correct"] or r["test_correct"])]

    def _stats(name, vals):
        if not vals:
            print(f"  {name}: n=0")
            return
        print(f"  {name}: n={len(vals)}  mean={sum(vals)/len(vals):.3f}  min={min(vals):.2f}  max={max(vals):.2f}")

    _stats("Correct passes  ", correct_confs)
    _stats("Incorrect passes", incorrect_confs)

    # ── CSV output ───────────────────────────────────────────────────────
    out_path = Path("analyze_run13_confidence_vs_correctness_c4_c8_results.csv")
    if all_rows:
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nDetailed results -> {out_path}")


if __name__ == "__main__":
    main()
