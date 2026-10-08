#!/usr/bin/env python3
"""
Reconstruct per-case JSON files from existing materialization experiment logs.

Reads AUTOSUGGEST and NEW_CRITIQUE logs to extract final Python code, combines
with cost/latency/is_correct from results CSVs, and writes one JSON per case
into a jsons/ directory under each experiment folder.

The JSON format matches what critique_data.py currently generates, so the same
analysis tooling can consume both old and new experiment outputs.

Key parsing rules
-----------------
AUTOSUGGEST logs: contain multiple "Get Python Script" blocks (one per
  intermediate materialization step, one final). The FINAL code is identified
  by the prompt containing "target_multisource.csv" (not "intermediate_step").
NEW_CRITIQUE logs: contain an operator-selection block followed by a code-
  refinement block. The final executable code is the last ```Python``` block
  that writes to "target_multisource_critique_history.csv".
Critique type ordering: fd=first log by timestamp, metadata=second, anonymization=third.

Results CSV column layout (header is misaligned with actual data in old runs):
  multi_step.csv  : case_id, is_correct, cost, latency, score_old, op_hist
  critique.csv    : case_id, ctype, is_correct, cost, latency, score_old
"""

import os
import re
import json
import csv
from datetime import datetime

BASE_LOG_DIR = "logs-auto-suggest-llm-21-04"
CRITIQUE_TYPES = ["fd", "metadata", "anonymization"]


# ---------------------------------------------------------------------------
# Log parsing helpers
# ---------------------------------------------------------------------------

def _extract_python_blocks(content):
    """Return all ```Python...``` code blocks found in content."""
    return re.findall(r"```[Pp]ython\s*(.*?)```", content, re.DOTALL)


def _sum_costs(content):
    """Sum all 'total_cost' values found in log content."""
    costs = re.findall(r"'total_cost':\s*([0-9.e+\-]+)", content)
    return sum(float(c) for c in costs)


def _log_latency(content):
    """Return elapsed seconds between first and last timestamp in log."""
    timestamps = re.findall(
        r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content, re.MULTILINE
    )
    if len(timestamps) < 2:
        return 0.0
    fmt = "%Y-%m-%d %H:%M:%S"
    return (
        datetime.strptime(timestamps[-1], fmt)
        - datetime.strptime(timestamps[0], fmt)
    ).total_seconds()


def parse_autosuggest_log(log_path):
    """
    Extract the FINAL Python code and operation history from an AUTOSUGGEST log.

    The final script is the Get Python Script block whose prompt mentions
    'target_multisource.csv' but NOT 'intermediate_step' — i.e. the one that
    produces the actual output, not an intermediate materialisation step.

    Returns (code: str, operation_history: str, total_cost: float, latency: float).
    """
    with open(log_path) as f:
        content = f.read()

    total_cost = _sum_costs(content)
    latency = _log_latency(content)
    operation_history = ""

    lines = content.splitlines()
    gps_indices = [
        i for i, ln in enumerate(lines)
        if "Query of Type : Get Python Script" in ln
    ]

    final_code = ""
    for gps_idx in gps_indices:
        # Find the "Result Recieved" line that follows this query block
        result_idx = None
        for j in range(gps_idx + 1, min(gps_idx + 600, len(lines))):
            if "Result Recieved" in lines[j]:
                result_idx = j
                break
        if result_idx is None:
            continue

        prompt_block = "\n".join(lines[gps_idx:result_idx])

        # Skip intermediate materialisation prompts
        is_final = (
            "target_multisource.csv" in prompt_block
            and "intermediate_step" not in prompt_block
        )
        if not is_final:
            continue

        # Extract operation history from this prompt
        m = re.search(
            r"Operation History:\s*(\[.*?\])", prompt_block, re.DOTALL
        )
        if m:
            operation_history = m.group(1).strip()

        # Extract code from the Result Recieved block
        result_block = "\n".join(lines[result_idx: min(result_idx + 300, len(lines))])
        code_blocks = _extract_python_blocks(result_block)
        if code_blocks:
            final_code = code_blocks[0].strip()

    # Fallback: if no "final" block found, take the very last code block in the log
    if not final_code:
        all_blocks = _extract_python_blocks(content)
        if all_blocks:
            final_code = all_blocks[-1].strip()

    return final_code, operation_history, total_cost, latency


def parse_critique_log(log_path):
    """
    Extract the final executable Python code from a NEW_CRITIQUE log.

    The critique log has two LLM calls:
      1. Operator-selection call — may embed a code example but it is NOT the
         final runnable script.
      2. Code-refinement call — produces the actual executable script that
         writes to target_multisource_critique_history.csv.

    We take the last ```Python``` block that contains a to_csv() call
    (the runnable script), falling back to the very last code block.

    Returns (code: str, total_cost: float, latency: float).
    """
    with open(log_path) as f:
        content = f.read()

    total_cost = _sum_costs(content)
    latency = _log_latency(content)

    all_blocks = _extract_python_blocks(content)

    final_code = ""
    for block in reversed(all_blocks):
        if "to_csv(" in block:
            final_code = block.strip()
            break

    if not final_code and all_blocks:
        final_code = all_blocks[-1].strip()

    return final_code, total_cost, latency


# ---------------------------------------------------------------------------
# CSV result loaders
# ---------------------------------------------------------------------------

def _bool(val):
    return str(val).strip().lower() == "true"


def _float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def load_ms_results(results_dir):
    """
    Load multi_step.csv.

    Old CSV layout (header is misaligned, parse by position):
      col 0: case_id   col 1: is_correct   col 2: cost
      col 3: latency   col 4: score_old    col 5: operation_history
    """
    results = {}
    path = os.path.join(results_dir, "multi_step.csv")
    if not os.path.exists(path):
        return results
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 2:
                continue
            case_id = row[0].strip()
            results[case_id] = {
                "is_correct": _bool(row[1]) if len(row) > 1 else False,
                "cost":       _float(row[2]) if len(row) > 2 else 0.0,
                "latency":    _float(row[3]) if len(row) > 3 else 0.0,
                "score_old":  _float(row[4]) if len(row) > 4 else 0.0,
            }
    return results


def load_critique_results(results_dir):
    """
    Load critique.csv.

    Old CSV layout (header is misaligned, parse by position):
      col 0: case_id   col 1: ctype   col 2: is_correct
      col 3: cost      col 4: latency col 5: score_old
    """
    results = {}
    path = os.path.join(results_dir, "critique.csv")
    if not os.path.exists(path):
        return results
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 3:
                continue
            case_id = row[0].strip()
            ctype   = row[1].strip()
            key = (case_id, ctype)
            results[key] = {
                "is_correct": _bool(row[2]) if len(row) > 2 else False,
                "cost":       _float(row[3]) if len(row) > 3 else 0.0,
                "latency":    _float(row[4]) if len(row) > 4 else 0.0,
                "score_old":  _float(row[5]) if len(row) > 5 else 0.0,
            }
    return results


# ---------------------------------------------------------------------------
# Experiment directory processor
# ---------------------------------------------------------------------------

def _parse_case_id(filename):
    """
    Extract (length, target_id, timestamp) from log filenames like:
      1_target50_AUTOSUGGEST_20260318_172808.log
      1_target54_NEW_CRITIQUE_20260318_173245.log
    Returns (case_id: str, timestamp: str) or (None, None).
    """
    m = re.match(
        r"(\d+)_target(\d+)_(?:AUTOSUGGEST|NEW_CRITIQUE)_(\d{8}_\d{6})\.log",
        filename,
    )
    if not m:
        return None, None
    length, target, ts = m.groups()
    return f"{length}_{target}", ts


def process_experiment_dir(exp_dir):
    logs_dir    = os.path.join(exp_dir, "logs")
    results_dir = os.path.join(exp_dir, "results")
    jsons_dir   = os.path.join(exp_dir, "jsons")
    os.makedirs(jsons_dir, exist_ok=True)

    ms_results   = load_ms_results(results_dir)
    crit_results = load_critique_results(results_dir)

    # Collect log paths grouped by case
    autosuggest_logs = {}   # case_id -> path
    critique_log_map = {}   # case_id -> [(timestamp, path), ...]

    for fname in sorted(os.listdir(logs_dir)):
        if not fname.endswith(".log"):
            continue
        case_id, ts = _parse_case_id(fname)
        if case_id is None:
            continue
        full_path = os.path.join(logs_dir, fname)
        if "AUTOSUGGEST" in fname:
            autosuggest_logs[case_id] = full_path
        elif "NEW_CRITIQUE" in fname:
            critique_log_map.setdefault(case_id, []).append((ts, full_path))

    # Sort critique logs by timestamp so fd < metadata < anonymization
    for case_id in critique_log_map:
        critique_log_map[case_id].sort(key=lambda x: x[0])

    written = 0
    for case_id, as_log in autosuggest_logs.items():
        ms_code, op_hist, ms_cost_log, ms_lat_log = parse_autosuggest_log(as_log)

        ms_res = ms_results.get(case_id, {})
        ms_entry = {
            "is_correct":         ms_res.get("is_correct", False),
            "score_old":          ms_res.get("score_old", 0.0),
            "score":              0.0,   # needs recomputation with new scoring
            "cost":               ms_res.get("cost", ms_cost_log),
            "latency":            ms_res.get("latency", ms_lat_log),
            "nl_score":           "",
            "generated_samples":  "",
            "code":               ms_code,
            "generated_csv_head": "",
            "operation_history":  op_hist,
        }

        crit_entries = []
        for i, (ts, crit_path) in enumerate(critique_log_map.get(case_id, [])):
            ctype = CRITIQUE_TYPES[i] if i < len(CRITIQUE_TYPES) else f"critique_{i}"
            crit_code, crit_cost_log, crit_lat_log = parse_critique_log(crit_path)

            cr = crit_results.get((case_id, ctype), {})
            crit_entries.append({
                "type":              ctype,
                "is_correct":        cr.get("is_correct", False),
                "score_old":         cr.get("score_old", 0.0),
                "score":             0.0,   # needs recomputation
                "cost":              cr.get("cost", crit_cost_log),
                "latency":           cr.get("latency", crit_lat_log),
                "nl_score":          "",
                "generated_samples": "",
                "code":              crit_code,
            })

        case_record = {
            "case": case_id,
            "iterations": [
                {
                    "iteration": 1,
                    "ms":        ms_entry,
                    "critiques": crit_entries,
                }
            ],
        }

        json_path = os.path.join(jsons_dir, f"{case_id}.json")
        tmp_path  = json_path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(case_record, f, indent=2, default=str)
        os.replace(tmp_path, json_path)
        written += 1

    print(f"  {exp_dir}: wrote {written} JSON files to {jsons_dir}")
    return written


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    total = 0
    for name in sorted(os.listdir(BASE_LOG_DIR)):
        if "ms_mat" not in name:
            continue
        exp_dir = os.path.join(BASE_LOG_DIR, name)
        if not os.path.isdir(exp_dir):
            continue
        print(f"\nProcessing: {name}")
        total += process_experiment_dir(exp_dir)
    print(f"\nDone. Total JSON files written: {total}")


if __name__ == "__main__":
    main()
