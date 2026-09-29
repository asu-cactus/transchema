#!/usr/bin/env python3
"""
oracle_validate.py — Oracle metric for the reward-function ablation study (Ablation Plan §1).

For each case in a results_langraph experiment, re-executes every FULL pipeline script the
MCTS search actually ran successfully during that case (every "[simulate/pipeline] Trial N:
execute_python='Success'" occurrence in the case's log — the simulate-path candidate scripts,
not critique's echoed/revised text or partial-pipeline executions). Since every ablation run
here uses --data_split training, the project's own is_correct is computed on the TEST-swapped
script (training_N.csv -> test_N.csv; see util.utils.make_test_validation_script), not on the
training execution -- Oracle mirrors that exactly: swap, re-execute, then validate the fresh
test-split output against ground truth with the SAME validator the project uses for its
official accuracy numbers (validation/hard_match.py's compare_tables_matching, i.e.
--validation autopipeline).

A case counts Oracle-correct if ANY re-executed script matches ground truth. This measures
whether the underlying MCTS SEARCH ever generated a correct pipeline for a case, independent of
whether the (possibly reward-component-ablated) scorer was able to SELECT it as the best-scoring
one -- an upper bound decoupled from the ablation's selection quality.

Scope note: only simulate-path scripts are counted (not critique-revised scripts) -- this is a
conservative choice, a slight possible UNDERCOUNT (missing a case where only a critique revision,
never the original simulate script, was correct), never an overcount, and it's what stays cleanly
and unambiguously parseable from the log format.

Safety: never touches any shared/production output path. Every to_csv() call inside a
re-executed script that targets a "target_multisource_mcts*" path is monkey-patched to a private
scratch file instead, regardless of how the script builds that path internally.

Usage:
    python3 oracle_validate.py --benchmark github --exp_name github_abl_wofd_dmx-gpt-oss-120b
    python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_wofd_dmx-gpt-oss-120b

Writes <exp_name>_oracle.csv (case_id, oracle_correct, n_scripts_tried, n_scripts_matched) next
to this script, and prints the summary count. Run from the repo root (or anywhere -- it chdirs
to its own directory so the benchmark-relative paths inside extracted scripts resolve correctly).
"""
import argparse
import csv
import glob
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_HERE)
sys.path.insert(0, _HERE)

import pandas as pd
from tqdm.auto import tqdm

from util.utils import execute_python, drop_leading_index_col_if_present, make_test_validation_script
from validation.hard_match import compare_tables_matching

_BENCHMARK_FOLDERS = {
    "github": "autopipeline-benchmarks/github-pipelines",
    "smart_building_v2": "autopipeline-benchmarks/smartbuilding-pipelines-v2-split",
}

_SCRATCH_DIR = "/tmp/oracle_validate_scratch"
os.makedirs(_SCRATCH_DIR, exist_ok=True)

# ── Redirect every "target_multisource_mcts*" write to a private scratch path ──────────
# Never let a re-executed historical script overwrite the shared production output file
# (some other experiment could be actively scoring the same case_id right now).
_current_scratch_path = {"path": None}
_orig_to_csv = pd.DataFrame.to_csv


def _patched_to_csv(self, path_or_buf=None, *args, **kwargs):
    if isinstance(path_or_buf, (str, os.PathLike)) and "target_multisource_mcts" in str(path_or_buf):
        path_or_buf = _current_scratch_path["path"]
    return _orig_to_csv(self, path_or_buf, *args, **kwargs)


pd.DataFrame.to_csv = _patched_to_csv

_CODE_BLOCK_RE = re.compile(r"```[Pp]ython\n(.*?)\n```", re.DOTALL)
_TRIAL_SUCCESS_RE = re.compile(r"\[simulate/pipeline\] Trial \d+: execute_python='Success'")
_MAX_BACKWARD_GAP = 2000  # chars between a code block's closing fence and its Trial-success line

# Critique-revised scripts have no "Trial N:" confirmation line. Two anchors instead:
# the real revised script is the fenced block immediately after "$END_CONFIDENCE$" (the
# echoed "Current Python script:" block earlier in the same response is NOT this), and
# its execution succeeded iff the components dict logged after it is a real dict, not None
# (components=None only happens on an execution/scoring error -- see _score_and_validate_output).
_END_CONFIDENCE_RE = re.compile(r"\$END_CONFIDENCE\$")
_MAX_FORWARD_GAP_CODE = 300     # chars between $END_CONFIDENCE$ and the code block after it
_COMPONENTS_OUTCOME_RE = re.compile(r"components=(None|\{)")
_MAX_FORWARD_GAP_OUTCOME = 5000  # chars between the code block and its components= outcome


def extract_successful_simulate_scripts(log_text: str) -> list:
    """Every fenced ```python block immediately confirmed by a simulate-path
    'Trial N: execute_python=Success' line (see module docstring for scope)."""
    scripts = []
    seen_spans = set()
    for trial_match in _TRIAL_SUCCESS_RE.finditer(log_text):
        preceding = log_text[: trial_match.start()]
        code_matches = list(_CODE_BLOCK_RE.finditer(preceding))
        if not code_matches:
            continue
        last = code_matches[-1]
        if trial_match.start() - last.end() > _MAX_BACKWARD_GAP:
            continue
        if last.span() in seen_spans:
            continue
        seen_spans.add(last.span())
        scripts.append(last.group(1))
    return scripts


def extract_successful_critique_scripts(log_text: str) -> list:
    """Every fenced ```python block that is the critique's REVISED script (anchored on
    the preceding $END_CONFIDENCE$, which the echoed 'Current Python script:' block does
    NOT have), confirmed successful by a following components={...} (not components=None)."""
    scripts = []
    seen_spans = set()
    for conf_match in _END_CONFIDENCE_RE.finditer(log_text):
        after = log_text[conf_match.end():]
        code_match = _CODE_BLOCK_RE.search(after)
        if not code_match or code_match.start() > _MAX_FORWARD_GAP_CODE:
            continue
        code_end_abs = conf_match.end() + code_match.end()
        outcome_match = _COMPONENTS_OUTCOME_RE.search(log_text, code_end_abs, code_end_abs + _MAX_FORWARD_GAP_OUTCOME)
        if not outcome_match or outcome_match.group(1) != "{":
            continue
        span = (conf_match.end() + code_match.start(), code_end_abs)
        if span in seen_spans:
            continue
        seen_spans.add(span)
        scripts.append(code_match.group(1))
    return scripts


# compare_tables()/compare_series() (validation/autopipeline_match.py) do a pure-Python
# per-element loop inside a for-col_target/for-col_generate nested loop -- O(rows * cols^2).
# Production only validates once per case (the selected best script); Oracle validates every
# successfully-run candidate script per case, multiplying that cost. On this project's own
# benchmarks, target.csv row counts are heavy-tailed (p95 ~50k, max 13.2M rows) -- a handful of
# cases at that tail pushed sustained aggregate memory past the ablation.slice ceiling and got
# OOM-killed (2026-09-28), taking the whole batch down with them. Skip those cases' Oracle
# check rather than let one case's pathological data blow up memory for everything running in
# the same cgroup; the row-count cutoff is a hard cap, not a probabilistic guess.
_MAX_GT_ROWS_FOR_ORACLE = 20_000


def validate_case(benchmark: str, case_label: str, log_paths: list) -> dict:
    """case_label e.g. '6_15' (length_caseid)."""
    length_str, case_id = case_label.split("_", 1)
    mf = _BENCHMARK_FOLDERS[benchmark]
    case_folder = f"{mf}/length{length_str}_{case_id}"
    gt_path = f"{case_folder}/target.csv"
    if not os.path.exists(gt_path):
        return {"case_id": case_label, "oracle_correct": "", "n_tried": 0, "n_matched": 0, "note": "no ground truth found"}

    df_gt = pd.read_csv(gt_path, low_memory=False)
    df_gt = drop_leading_index_col_if_present(df_gt)

    if len(df_gt) > _MAX_GT_ROWS_FOR_ORACLE:
        return {
            "case_id": case_label, "oracle_correct": "", "n_tried": 0, "n_matched": 0,
            "note": f"skipped: ground truth has {len(df_gt)} rows (> {_MAX_GT_ROWS_FOR_ORACLE}) -- compare_tables() is O(rows*cols^2) and OOM'd the batch on this size",
        }

    all_scripts = []  # list of (source, script_text)
    for lp in log_paths:
        with open(lp, errors="replace") as f:
            text = f.read()
        all_scripts.extend(("simulate", s) for s in extract_successful_simulate_scripts(text))
        all_scripts.extend(("critique", s) for s in extract_successful_critique_scripts(text))

    n_matched = 0
    oracle_correct = False
    matched_source = ""
    for i, (source, script) in enumerate(all_scripts):
        # data_split=training's official is_correct is computed on the TEST-swapped
        # script (training_N.csv -> test_N.csv, output -> *_test_val.csv), not on the
        # training execution itself -- see util.utils.make_test_validation_script's
        # docstring/history. Oracle must use the identical definition of "correct" the
        # project already uses everywhere else, so swap+execute the test variant here.
        test_script = make_test_validation_script(script)
        scratch_path = os.path.join(_SCRATCH_DIR, f"{case_label}_{i}.csv")
        _current_scratch_path["path"] = scratch_path
        if os.path.exists(scratch_path):
            os.remove(scratch_path)
        try:
            result = execute_python(test_script)
            if result != "Success" or not os.path.exists(scratch_path):
                continue
            # A buggy candidate script (e.g. an accidental cross-join) can produce a huge
            # output even when the real ground truth is tiny -- the _MAX_GT_ROWS_FOR_ORACLE
            # guard above only catches an oversized ground truth, not this. Cheap line-count
            # first (no pandas load) so a pathological output never reaches compare_tables_matching.
            with open(scratch_path, "rb") as _sf:
                _out_lines = sum(1 for _ in _sf)
            if _out_lines > _MAX_GT_ROWS_FOR_ORACLE:
                continue
            df_out = pd.read_csv(scratch_path, low_memory=False)
            _, is_match, _, _ = compare_tables_matching(df_out, df_gt)
            if is_match:
                n_matched += 1
                oracle_correct = True
                matched_source = source
                break  # short-circuit: case is Oracle-correct, no need to try the rest
        except Exception:
            continue
        finally:
            if os.path.exists(scratch_path):
                os.remove(scratch_path)

    n_simulate = sum(1 for s, _ in all_scripts if s == "simulate")
    n_critique = len(all_scripts) - n_simulate
    return {
        "case_id": case_label, "oracle_correct": oracle_correct, "n_tried": len(all_scripts),
        "n_matched": n_matched, "note": f"n_simulate={n_simulate} n_critique={n_critique} matched_source={matched_source}",
    }


def _validate_case_worker(task: tuple) -> dict:
    """Top-level (picklable) wrapper for multiprocessing.Pool workers."""
    benchmark, case_label, log_paths = task
    try:
        return validate_case(benchmark, case_label, log_paths)
    except Exception as e:
        return {"case_id": case_label, "oracle_correct": "", "n_tried": 0, "n_matched": 0, "note": f"worker exception: {e}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", required=True, choices=["github", "smart_building_v2"])
    ap.add_argument("--exp_name", required=True, help="e.g. github_abl_wofd_dmx-gpt-oss-120b")
    ap.add_argument("--only_case", default="", help="debug: validate a single case_id (e.g. 6_15) and exit")
    ap.add_argument("--workers", type=int, default=1, help="parallel worker processes (e.g. 40); each grabs the next case as soon as it's free")
    args = ap.parse_args()

    log_root = f"logs_langraph/{args.exp_name}"
    case_dirs = sorted(glob.glob(f"{log_root}/cases_g*_c*"))
    if not case_dirs:
        print(f"ERROR: no case log dirs found under {log_root}")
        sys.exit(1)

    _CASE_DIR_RE = re.compile(r"cases_g(\d+)_c(\d+)$")
    cases = {}  # case_label -> list of log paths
    for cd in case_dirs:
        m = _CASE_DIR_RE.search(cd)
        if not m:
            continue
        case_label = f"{m.group(1)}_{m.group(2)}"
        logs = sorted(glob.glob(f"{cd}/*_MCTS_*.log"))
        if logs:
            cases[case_label] = logs

    if args.only_case:
        cases = {args.only_case: cases[args.only_case]} if args.only_case in cases else {}
        if not cases:
            print(f"ERROR: case {args.only_case} not found under {log_root}")
            sys.exit(1)

    ordered_cases = sorted(cases.items(), key=lambda kv: (int(kv[0].split('_')[0]), int(kv[0].split('_')[1])))

    # --only_case is a debug tool -- it must NEVER touch the real <exp>_oracle.csv (which may
    # hold real, expensive-to-recompute progress from the actual run). Write-mode logic below
    # truncates out_csv when there's nothing to resume from, and --only_case's cases dict is a
    # single case that was never meant to represent (or replace) the whole experiment.
    out_csv = (
        f"{args.exp_name}_oracle_debug_{args.only_case}.csv" if args.only_case
        else f"{args.exp_name}_oracle.csv"
    )
    fieldnames = ["case_id", "oracle_correct", "n_tried", "n_matched", "note"]

    # Resume: a prior run's (or the watchdog's relaunch of a) out_csv already has rows for
    # some cases -- skip those unless --only_case forces a specific one to redo. Since
    # oracle_validate.py re-executes real scripts (a case with a wide/expensive table can take
    # a while), redoing already-done cases on every relaunch wastes real time, not just a
    # cheap resume check.
    done_rows = {}
    if not args.only_case and os.path.exists(out_csv):
        with open(out_csv, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("case_id"):
                    done_rows[row["case_id"]] = row

    remaining = [(cl, lp) for cl, lp in ordered_cases if cl not in done_rows]
    n_skipped = len(ordered_cases) - len(remaining)
    print(f"{len(cases)} cases with logs under {log_root} -- {args.workers} worker(s)"
          + (f" -- resuming: {n_skipped} already done, {len(remaining)} remaining" if n_skipped else ""))

    tasks = [(args.benchmark, case_label, log_paths) for case_label, log_paths in remaining]

    rows = list(done_rows.values())
    n_oracle_correct = sum(1 for r in rows if r.get("oracle_correct") == "True")

    # Append if resuming (done_rows came from this exact file), otherwise start fresh.
    write_mode = "a" if done_rows else "w"
    with open(out_csv, write_mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_mode == "w":
            w.writeheader()
        f.flush()

        if args.workers <= 1:
            result_iter = (_validate_case_worker(t) for t in tasks)
        else:
            import multiprocessing
            pool = multiprocessing.Pool(processes=args.workers)
            result_iter = pool.imap_unordered(_validate_case_worker, tasks)

        pbar = tqdm(total=len(ordered_cases), initial=n_skipped, desc=args.exp_name, unit="case")
        for r in result_iter:
            rows.append(r)
            if r["oracle_correct"] is True:
                n_oracle_correct += 1
            w.writerow(r)
            f.flush()
            pbar.set_postfix(oracle_correct=n_oracle_correct)
            pbar.update(1)
        pbar.close()

        if args.workers > 1:
            pool.close()
            pool.join()

    n_total = len(rows)
    print(f"\n{args.exp_name}: Oracle {n_oracle_correct}/{n_total} = {100*n_oracle_correct/n_total:.1f}%")
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()
