"""patch_critique.py

Evaluates every case in --jsons_dir using iteration-1 data only.

Pipeline per case (judge configured via --judge):
  1. Restore MS output, run judge.
       judge=True  → final = ms.is_correct
       judge=False → step 2
  2. Ensure critiques[0] exists (invoke crit() from MS state if absent).
     Restore critiques[0] output, run judge.
       judge=True  → final = critiques[0].is_correct
       judge=False → step 3
  3. critiques[1] must already exist (no further invocation).
     Restore critiques[1] output, run judge.
       judge=True  → final = critiques[1].is_correct
       judge=False → final = False

Only iteration 1 is considered. Critique data is judge-agnostic: reused if already
stored in the JSON, freshly invoked (and stored back) only when absent.

Metrics written to patch_results/results/summary_{judge}.csv:
  - final_is_correct, ms_is_correct, judge_calls, critique_invoked
  - ms_cost / ms_latency: from stored JSON
  - judge_cost / judge_latency: accumulated over all judge calls this run
  - critique_cost / critique_latency: stored critique costs + any newly invoked
  - total_cost / total_latency: ms + judge + critique

Usage:
    python patch_critique.py --jsons_dir path/to/jsons_v3 --judge llm [critique_data.py args]
"""

import os
import csv
import json
import time
import traceback
import tempfile
import subprocess
import multiprocessing

import pandas as pd

from critique_data import crit, _flush_json, get_parser as _base_get_parser
from log_util.log_util import create_logger
from judges import judge as run_judge
from llm.llm_models import LLMClient, TokenUsageTracker


_CASE_TIMEOUT = 600  # seconds, matches critique_data.py

_SUMMARY_FIELDS = [
    "case",
    "judge",
    "ms_judge_says_correct",
    "judge_calls",
    "critique_invoked",
    "final_is_correct",
    "ms_is_correct",
    "ms_cost",
    "ms_latency",
    "judge_cost",
    "judge_latency",
    "critique_cost",
    "critique_latency",
    "total_cost",
    "total_latency",
]


def get_parser():
    parser = _base_get_parser()
    parser.add_argument(
        "--jsons_dir",
        type=str,
        required=True,
        help="Path to the jsons directory to evaluate.",
    )
    parser.set_defaults(validation="autopipeline")
    return parser


def _run_code(code):
    """Execute code in a temp file; return subprocess.CompletedProcess."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        return subprocess.run(
            ["python3", tmp_path],
            capture_output=True, text=True, timeout=120,
        )
    finally:
        os.unlink(tmp_path)


def _patch_worker(args, json_path, result_queue):
    try:
        _bn = os.path.basename(json_path)
        case_name = _bn.replace(".json.tmp", "").replace(".json", "")
        parts = case_name.split("_")
        length = int(parts[0])
        id_ = int(parts[1])

        with open(json_path) as f:
            case_record = json.load(f)

        iter1 = None
        iter1_idx = None
        for i, it in enumerate(case_record.get("iterations", [])):
            if it["iteration"] == 1:
                iter1 = it
                iter1_idx = i
                break

        if iter1 is None:
            print(f"[{case_name}] No iteration 1 found, skipping")
            result_queue.put(("skip", None))
            return

        ms_code = iter1["ms"].get("code", "")
        if not ms_code:
            print(f"[{case_name}] No ms code stored, skipping")
            result_queue.put(("skip", None))
            return

        ms_cost = float(iter1["ms"].get("cost", 0.0))
        ms_latency = float(iter1["ms"].get("latency", 0.0))
        ms_is_correct = bool(iter1["ms"].get("is_correct", False))

        main_folder_base = (
            "autopipeline-benchmarks/monteprep-pipelines"
            if getattr(args, "benchmark", "github") == "monteprep"
            else "autopipeline-benchmarks/github-pipelines"
        )
        case_path = f"{length}_{id_}"
        gt_path = f"{main_folder_base}/length{case_path}/target.csv"
        generated_path = f"{main_folder_base}/length{case_path}/target_multisource.csv"

        # Shared judge client — cumulates cost across all calls for this case
        _judge_tracker = TokenUsageTracker()
        _case_logger = create_logger("PATCH_JUDGE", args.log_directory, length, id_, id_)
        _judge_client = LLMClient(model=args.model, tracker=_judge_tracker, logger=_case_logger)
        judge_latency_total = 0.0
        judge_calls = 0

        def _judge_on(code):
            """Execute code, load CSVs, run judge. Returns (is_correct, reason)."""
            nonlocal judge_latency_total, judge_calls
            exec_res = _run_code(code)
            if exec_res.returncode != 0:
                return False, f"exec failed: {exec_res.stderr[:200]}"
            df_gen = pd.read_csv(generated_path, low_memory=False)
            df_gt = pd.read_csv(gt_path, low_memory=False)
            df_gt.drop(columns=df_gt.columns[0], axis=1, inplace=True)
            t0 = time.time()
            ok, reason = run_judge(df_gen, df_gt, args.judge, _judge_client, logger=_case_logger)
            judge_latency_total += time.time() - t0
            judge_calls += 1
            return ok, reason

        critique_cost_total = 0.0
        critique_latency_total = 0.0
        critique_invoked = False

        def _invoke_single_crit(restore_code, crit_type, judge_reason):
            """Restore state, invoke crit() for one type, return list of entries (may be 0 or 1)."""
            nonlocal critique_invoked
            exec_res = _run_code(restore_code)
            if exec_res.returncode != 0:
                print(f"[{case_name}] Code exec failed restoring state for {crit_type}")
                return [], 0.0, 0.0
            orig_setting = args.critique_setting
            args.critique_setting = [crit_type]
            _, attempts = crit(
                args, length, id_,
                operation_history="",
                past_context_str="",
                judge_reason=judge_reason,
            )
            args.critique_setting = orig_setting
            critique_invoked = True
            entries = [
                {
                    "type": a["type"],
                    "is_correct": bool(a["is_correct"]),
                    "score": float(a.get("score", 0.0)),
                    "cost": float(a.get("cost", 0.0)),
                    "latency": float(a.get("latency", 0.0)),
                    "nl_score": a.get("nl_score", ""),
                    "generated_samples": a.get("generated_samples", ""),
                    "code": a.get("code", ""),
                    "patch_judge": args.judge,
                }
                for a in attempts
            ]
            inv_cost = sum(float(a.get("cost", 0.0)) for a in attempts)
            inv_lat = sum(float(a.get("latency", 0.0)) for a in attempts)
            return entries, inv_cost, inv_lat

        # ── Step 1: judge on MS output ───────────────────────────────────────
        ms_ok, ms_reason = _judge_on(ms_code)
        print(f"[{case_name}] MS judge={ms_ok}")

        if ms_ok:
            final_is_correct = ms_is_correct

        else:
            crits = list(iter1.get("critiques", []))

            # ── Ensure critiques[0] (fd) — invoke only if absent ────────────
            if len(crits) == 0 or not crits[0].get("code"):
                print(f"[{case_name}] fd critique absent — invoking")
                new_entries, inv_cost, inv_lat = _invoke_single_crit(ms_code, "fd", ms_reason)
                if not new_entries:
                    print(f"[{case_name}] fd invocation yielded nothing — incorrect")
                    final_is_correct = False
                    judge_cost_total = _judge_tracker.cost_summary()["total_cost"]
                    result_queue.put(("ok", {
                        "case": case_name, "judge": args.judge,
                        "ms_judge_says_correct": ms_ok, "judge_calls": judge_calls,
                        "critique_invoked": critique_invoked, "final_is_correct": False,
                        "ms_is_correct": ms_is_correct,
                        "ms_cost": ms_cost, "ms_latency": ms_latency,
                        "judge_cost": judge_cost_total, "judge_latency": judge_latency_total,
                        "critique_cost": inv_cost, "critique_latency": inv_lat,
                        "total_cost": ms_cost + judge_cost_total + inv_cost,
                        "total_latency": ms_latency + judge_latency_total + inv_lat,
                    }))
                    return
                crits = new_entries  # may include both fd and metadata if crit() returned both
                critique_cost_total += inv_cost
                critique_latency_total += inv_lat
                case_record["iterations"][iter1_idx]["critiques"] = crits
                _flush_json(case_record, json_path)
                print(f"[{case_name}] Stored {len(crits)} critique(s) from fd invocation")
            else:
                critique_cost_total += float(crits[0].get("cost", 0.0))

            # ── Step 2: judge on critiques[0] (fd) ──────────────────────────
            c0_ok, c0_reason = _judge_on(crits[0]["code"])
            print(f"[{case_name}] crit[0] ({crits[0]['type']}) judge={c0_ok}")

            if c0_ok:
                final_is_correct = bool(crits[0]["is_correct"])

            else:
                # ── Ensure critiques[1] (metadata) — invoke only if absent ──
                if len(crits) < 2 or not crits[1].get("code"):
                    print(f"[{case_name}] metadata critique absent — invoking from fd state")
                    new_entries, inv_cost, inv_lat = _invoke_single_crit(
                        crits[0]["code"], "metadata", c0_reason
                    )
                    critique_cost_total += inv_cost
                    critique_latency_total += inv_lat
                    if new_entries:
                        crits.append(new_entries[0])
                        case_record["iterations"][iter1_idx]["critiques"] = crits
                        _flush_json(case_record, json_path)
                        print(f"[{case_name}] metadata critique stored")
                else:
                    critique_cost_total += float(crits[1].get("cost", 0.0))
                    critique_latency_total += float(crits[1].get("latency", 0.0))

                # ── Step 3: judge on critiques[1] (metadata) ────────────────
                if len(crits) < 2 or not crits[1].get("code"):
                    print(f"[{case_name}] No metadata critique available — incorrect")
                    final_is_correct = False
                else:
                    c1_ok, _ = _judge_on(crits[1]["code"])
                    print(f"[{case_name}] crit[1] ({crits[1]['type']}) judge={c1_ok}")
                    if c1_ok:
                        final_is_correct = bool(crits[1]["is_correct"])
                    else:
                        print(f"[{case_name}] all judges incorrect — final=False")
                        final_is_correct = False

        judge_cost_total = _judge_tracker.cost_summary()["total_cost"]

        metrics = {
            "case": case_name,
            "judge": args.judge,
            "ms_judge_says_correct": ms_ok,
            "judge_calls": judge_calls,
            "critique_invoked": critique_invoked,
            "final_is_correct": final_is_correct,
            "ms_is_correct": ms_is_correct,
            "ms_cost": ms_cost,
            "ms_latency": ms_latency,
            "judge_cost": judge_cost_total,
            "judge_latency": judge_latency_total,
            "critique_cost": critique_cost_total,
            "critique_latency": critique_latency_total,
            "total_cost": ms_cost + judge_cost_total + critique_cost_total,
            "total_latency": ms_latency + judge_latency_total + critique_latency_total,
        }
        result_queue.put(("ok", metrics))

    except Exception:
        result_queue.put(("error", traceback.format_exc()))


if __name__ == "__main__":
    args = get_parser().parse_args()

    if args.judge == "gt":
        raise SystemExit(
            "Error: --judge 'gt' is not valid for patching (GT was the original judge; "
            "nothing to patch). Choose: llm, det_score, llm_score, llm_score_hybrid."
        )

    args.static_hints = not args.no_static_hints
    args.majority_voting = args.no_of_runs // 2 + 1

    # Create patch-specific log/results dirs alongside jsons_dir
    patch_base = os.path.join(
        os.path.dirname(os.path.abspath(args.jsons_dir.rstrip("/"))), "patch_results"
    )
    patch_logs = os.path.join(patch_base, "logs")
    patch_results = os.path.join(patch_base, "results")
    os.makedirs(patch_logs, exist_ok=True)
    os.makedirs(patch_results, exist_ok=True)

    # critique.csv expected by crit() → append mode so multiple judges coexist
    critique_csv = os.path.join(patch_results, "critique.csv")
    if not os.path.exists(critique_csv):
        with open(critique_csv, "w", newline="") as f:
            f.write("Length,Critique Type,Hard Match,Soft Match,Soft Acc,Cost,Latency,Score\n")

    args.log_directory = patch_logs
    args.result_directory = patch_results

    json_files = sorted(
        entry.path
        for entry in os.scandir(args.jsons_dir)
        if entry.name.endswith(".json") or entry.name.endswith(".json.tmp")
    )
    print(f"Found {len(json_files)} JSON files in {args.jsons_dir}")
    print(f"Judge: {args.judge} | Model: {args.model} | Validation: {args.validation}")
    print(f"Results → {patch_base}\n")

    all_metrics = []
    n_skipped = 0
    n_errors = 0

    for json_path in json_files:
        _bn = os.path.basename(json_path)
        case_name = _bn.replace(".json.tmp", "").replace(".json", "")
        print(f"Processing: {case_name}")

        _result_queue = multiprocessing.Queue()
        _proc = multiprocessing.Process(
            target=_patch_worker,
            args=(args, json_path, _result_queue),
            daemon=True,
        )
        _proc.start()
        _proc.join(timeout=_CASE_TIMEOUT)

        if _proc.is_alive():
            print(f"[TIMEOUT] {case_name} exceeded {_CASE_TIMEOUT}s — killing")
            _proc.terminate()
            _proc.join()
            n_errors += 1
        elif not _result_queue.empty():
            status, payload = _result_queue.get()
            if status == "ok":
                all_metrics.append(payload)
            elif status == "skip":
                n_skipped += 1
            else:
                print(f"Error for {case_name}:\n{payload}")
                n_errors += 1
        else:
            print(f"{case_name} exited without result")
            n_errors += 1

    # Write per-case summary CSV
    summary_csv = os.path.join(patch_results, f"summary_{args.judge}.csv")
    with open(summary_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(all_metrics)

    n = len(all_metrics)
    if n > 0:
        n_correct = sum(1 for m in all_metrics if m["final_is_correct"])
        n_critique_invoked = sum(1 for m in all_metrics if m["critique_invoked"])
        avg_judge_calls = sum(m["judge_calls"] for m in all_metrics) / n
        avg_ms_cost = sum(m["ms_cost"] for m in all_metrics) / n
        avg_judge_cost = sum(m["judge_cost"] for m in all_metrics) / n
        avg_crit_cost = sum(m["critique_cost"] for m in all_metrics) / n
        avg_total_cost = sum(m["total_cost"] for m in all_metrics) / n
        avg_ms_lat = sum(m["ms_latency"] for m in all_metrics) / n
        avg_judge_lat = sum(m["judge_latency"] for m in all_metrics) / n
        avg_crit_lat = sum(m["critique_latency"] for m in all_metrics) / n
        avg_total_lat = sum(m["total_latency"] for m in all_metrics) / n

        print(f"\n{'='*55}")
        print(f"Judge: {args.judge}  |  Cases evaluated: {n}")
        print(f"{'='*55}")
        print(f"Accuracy (final correct):    {n_correct} / {n}")
        print(f"Critique freshly invoked:    {n_critique_invoked} / {n}")
        print(f"Avg judge calls per case:    {avg_judge_calls:.2f}")
        print()
        print(f"Avg cost (MS + judge + critique):")
        print(f"  MS:        ${avg_ms_cost:.6f}")
        print(f"  Judge:     ${avg_judge_cost:.6f}")
        print(f"  Critique:  ${avg_crit_cost:.6f}")
        print(f"  Total:     ${avg_total_cost:.6f}")
        print()
        print(f"Avg latency (s):")
        print(f"  MS:        {avg_ms_lat:.2f}s")
        print(f"  Judge:     {avg_judge_lat:.2f}s")
        print(f"  Critique:  {avg_crit_lat:.2f}s")
        print(f"  Total:     {avg_total_lat:.2f}s")
        print(f"{'='*55}")
        print(f"Per-case CSV → {summary_csv}")

    print(f"\nDone. Evaluated: {n} | Skipped: {n_skipped} | Errors: {n_errors}")
