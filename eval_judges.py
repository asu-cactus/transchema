"""
Post-hoc judge evaluation script.

Reads JSON files produced by critique_data.py (--iterative N) and, for each case,
simulates 5 judge types independently:

  gt               — stop when is_correct == True (no LLM calls)
  det_score        — stop when stored score >= 1 - EPS (no LLM calls)
  llm              — LLM sees generated + ground truth tables
  llm_score        — LLM sees tables + numeric score
  llm_score_hybrid — LLM sees tables + NL score interpretation

For each judge type the script tracks:
  generation_cost / generation_latency  — cumulative from the JSON up to the stopping attempt
  judge_cost / judge_latency            — cumulative from LLM judge calls (0 for gt / det_score)
  total_cost / total_latency            — sum of the two

Output: one CSV row per (case, judge_type).

Usage:
  python eval_judges.py \
      --jsons_dir  logs/my_experiment/jsons \
      --output_csv logs/my_experiment/judge_eval.csv \
      --model      gpt-4.1-mini \
      --benchmark  github
"""

import argparse
import csv
import json
import logging
import os
import subprocess
import tempfile
import time
from glob import glob
from io import StringIO

import pandas as pd

from judges import score_judge, llm_judge, llm_score_judge, llm_nl_score_judge, EPS
from llm.llm_models import LLMClient, TokenUsageTracker
from eval_score_value_based import value_based_relative_csv_score_timed


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def get_parser():
    parser = argparse.ArgumentParser(description="Post-hoc judge evaluation over iterative experiment JSONs")
    parser.add_argument("--jsons_dir", type=str, required=True,
                        help="Directory containing per-case JSON files from critique_data.py")
    parser.add_argument("--output_csv", type=str, required=True,
                        help="Path to write the results CSV")
    parser.add_argument("--model", type=str, default="gpt-4.1-mini",
                        help="OpenAI model for LLM-based judges")
    parser.add_argument("--log_dir", type=str, default=None,
                        help="Directory for per-judge log files (default: <jsons_dir>/../logs_eval)")
    parser.add_argument("--benchmark", type=str, default="github", choices=["github", "monteprep"],
                        help="Benchmark dataset (used to reconstruct ground-truth path)")
    parser.add_argument("--max_iterations", type=int, default=None,
                        help="Maximum number of iterations the judge may check (default: all)")
    parser.add_argument("--judges", nargs="+", default=None,
                        choices=["gt", "det_score", "det_score_value", "llm", "llm_score", "llm_score_hybrid"],
                        help="Which judge types to run (default: all)")
    parser.add_argument("--score_source", type=str, default="score", choices=["score", "det_score"],
                        help="Which score to pass to llm_score and llm_score_hybrid judges: "
                             "'score' uses the stored score field, 'det_score' uses the value-based value_score field")
    return parser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

JUDGE_TYPES = ["gt", "det_score", "det_score_value", "llm", "llm_score", "llm_score_hybrid"]

OUTPUT_HEADER = [
    "case", "judge_type", "stopped_at", "stopped_correct",
    "generation_cost", "generation_latency",
    "judge_cost", "judge_latency",
    "total_cost", "total_latency",
]


def _gt_path(case_id: str, benchmark: str) -> str:
    folder = (
        "autopipeline-benchmarks/monteprep-pipelines"
        if benchmark == "monteprep"
        else "autopipeline-benchmarks/github-pipelines"
    )
    return f"{folder}/length{case_id}/target.csv"


def _load_gt(case_id: str, benchmark: str) -> pd.DataFrame:
    path = _gt_path(case_id, benchmark)
    df = pd.read_csv(path, low_memory=False)
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    return df


def _df_from_csv_head(csv_head: str) -> pd.DataFrame:
    """Reconstruct a DataFrame from the stored head(10) CSV string."""
    if not csv_head:
        return None
    return pd.read_csv(StringIO(csv_head), low_memory=False)


def flatten_attempts(case_data: dict) -> list:
    """
    Return an ordered list of attempt dicts:
      iter1_ms → iter1_<crit1> → iter1_<crit2> → iter2_ms → …
    Each dict has keys:
      label, iteration, attempt_type, is_correct, score,
      cost, latency, nl_score, generated_csv_head
    """
    attempts = []
    for iter_record in case_data.get("iterations", []):
        iter_num = iter_record["iteration"]
        ms = iter_record["ms"]
        attempts.append({
            "label": f"iter{iter_num}_ms",
            "iteration": iter_num,
            "attempt_type": "ms",
            "is_correct": ms.get("is_correct", False),
            "score": ms.get("score", 0.0),
            "value_score": ms.get("value_score"),
            "cost": ms.get("cost", 0.0),
            "latency": ms.get("latency", 0.0),
            "nl_score": ms.get("nl_score", ""),
            "generated_csv_head": ms.get("generated_csv_head", ""),
            "code": ms.get("code", ""),
        })
        for crit in iter_record.get("critiques", []):
            attempts.append({
                "label": f"iter{iter_num}_{crit['type']}",
                "iteration": iter_num,
                "attempt_type": crit["type"],
                "is_correct": crit.get("is_correct", False),
                "score": crit.get("score", 0.0),
                "value_score": crit.get("value_score"),
                "cost": crit.get("cost", 0.0),
                "latency": crit.get("latency", 0.0),
                "nl_score": crit.get("nl_score", ""),
                "generated_csv_head": crit.get("generated_csv_head", ""),
                "code": crit.get("code", ""),
            })
    return attempts


def _make_logger(log_dir: str, case_id: str, judge_type: str) -> logging.Logger:
    name = f"{case_id}_{judge_type}"
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    os.makedirs(log_dir, exist_ok=True)
    fh = logging.FileHandler(os.path.join(log_dir, f"{name}.log"), mode="w")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)
    return logger


def _execute_code_and_read_df(code: str, case_id: str, benchmark: str,
                               attempt_type: str = "ms",
                               timeout: int = 60) -> pd.DataFrame:
    """
    Write generated code to a temp file, execute it from the project root
    (so relative CSV paths resolve correctly), then read back the output CSV.
    - ms attempts write to target_multisource.csv
    - critique attempts (fd, metadata, …) write to target_multisource_critique_history.csv
    Returns None on timeout or any execution error.
    """
    if not code:
        return None

    folder = (
        "autopipeline-benchmarks/monteprep-pipelines"
        if benchmark == "monteprep"
        else "autopipeline-benchmarks/github-pipelines"
    )
    output_filename = (
        "target_multisource.csv" if attempt_type == "ms"
        else "target_multisource_critique_history.csv"
    )
    output_path = os.path.join(folder, f"length{case_id}", output_filename)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return None
        if not os.path.exists(output_path):
            return None
        return pd.read_csv(output_path, low_memory=False)
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Per-judge simulation
# ---------------------------------------------------------------------------

def simulate_judge(attempts: list, judge_type: str, df_gt: pd.DataFrame,
                   llm_client: LLMClient, logger: logging.Logger,
                   case_id: str = "", benchmark: str = "github",
                   score_source: str = "score") -> dict:
    """
    Iterate through attempts in order, asking the judge after each one.
    Returns a dict with the result fields.
    """
    generation_cost = 0.0
    generation_latency = 0.0
    judge_cost = 0.0
    judge_latency = 0.0
    stopped_at = None
    stopped_correct = False

    for attempt in attempts:
        generation_cost += attempt["cost"]
        generation_latency += attempt["latency"]
        label = attempt["label"]

        if judge_type == "gt":
            verdict = attempt["is_correct"]

        elif judge_type == "det_score":
            verdict = attempt["score"] >= (1.0 - EPS)
            logger.info(
                f"[det_score] {label}: score={attempt['score']:.4f}, "
                f"threshold={1.0 - EPS:.4f}, verdict={verdict}"
            )

        elif judge_type == "det_score_value":
            value_score = attempt.get("value_score")
            if value_score is None:
                logger.warning(f"[det_score_value] {label}: value_score not available, skipping")
                continue
            verdict = value_score >= (1.0 - EPS)
            logger.info(
                f"[det_score_value] {label}: value_score={value_score:.4f}, "
                f"threshold={1.0 - EPS:.4f}, verdict={verdict}"
            )

        else:  # LLM-based judges need the generated DataFrame
            csv_head = attempt.get("generated_csv_head", "")
            if not csv_head:
                logger.warning(f"[{judge_type}] {label}: no generated_csv_head, skipping")
                continue
            if df_gt is None:
                logger.warning(f"[{judge_type}] {label}: no ground truth, skipping")
                continue

            df_gen = _df_from_csv_head(csv_head)
            if df_gen is None or len(df_gen) == 0:
                logger.warning(f"[{judge_type}] {label}: empty generated DataFrame, skipping")
                continue

            cost_before = llm_client.tracker.cost_summary()["total_cost"]
            t0 = time.time()

            if judge_type == "llm":
                verdict, reason = llm_judge(df_gen, df_gt, llm_client, logger=logger)
            elif judge_type == "llm_score":
                precomputed = (
                    attempt.get("value_score") if score_source == "det_score"
                    else attempt.get("score")
                )
                verdict, reason = llm_score_judge(
                    df_gen, df_gt, llm_client, logger=logger,
                    precomputed_score=precomputed,
                )
            elif judge_type == "llm_score_hybrid":
                if score_source == "det_score":
                    vs = attempt.get("value_score")
                    precomputed_nl = str(round(vs, 4)) if vs is not None else None
                else:
                    precomputed_nl = attempt.get("nl_score") or None
                verdict, reason = llm_nl_score_judge(
                    df_gen, df_gt, llm_client, logger=logger,
                    precomputed_nl_score=precomputed_nl,
                )
            else:
                verdict, reason = False, ""

            call_latency = time.time() - t0
            call_cost = llm_client.tracker.cost_summary()["total_cost"] - cost_before
            judge_cost += call_cost
            judge_latency += call_latency

            logger.info(
                f"[{judge_type}] {label}: verdict={verdict}, reason={reason!r}, "
                f"call_cost={call_cost:.6f}, call_latency={call_latency:.2f}s"
            )

        if verdict:
            stopped_at = label
            stopped_correct = attempt["is_correct"]
            break

    # If judge never stopped, record the last attempt
    if stopped_at is None and attempts:
        stopped_at = attempts[-1]["label"]
        stopped_correct = attempts[-1]["is_correct"]

    return {
        "stopped_at": stopped_at or "none",
        "stopped_correct": stopped_correct,
        "generation_cost": generation_cost,
        "generation_latency": generation_latency,
        "judge_cost": judge_cost,
        "judge_latency": judge_latency,
        "total_cost": generation_cost + judge_cost,
        "total_latency": generation_latency + judge_latency,
    }


# ---------------------------------------------------------------------------
# Value-score pre-pass
# ---------------------------------------------------------------------------

def _patch_missing_value_scores(case_data: dict, df_gt: pd.DataFrame,
                                  case_id: str, benchmark: str, json_path: str) -> None:
    """
    For each attempt that lacks a 'value_score' key, execute its code, compute
    value_based_relative_csv_score_timed, and write 'value_score' back into
    case_data in place. Saves the JSON file to disk if any entries were added.
    """
    patched = 0
    for iter_record in case_data.get("iterations", []):
        entries = [("ms", iter_record["ms"])] + [
            (c.get("type", f"critique_{i}"), c)
            for i, c in enumerate(iter_record.get("critiques", []))
        ]
        for attempt_type, entry in entries:
            if "value_score" in entry:
                continue
            code = entry.get("code", "")
            if not code:
                entry["value_score"] = None
                patched += 1
                continue
            df_gen = _execute_code_and_read_df(code, case_id, benchmark,
                                               attempt_type=attempt_type)
            if df_gen is None or len(df_gen) == 0:
                entry["value_score"] = None
                patched += 1
                continue
            try:
                _, _, _, _, true_combined_score, _ = value_based_relative_csv_score_timed(df_gen, df_gt)
                entry["value_score"] = true_combined_score
            except TimeoutError:
                entry["value_score"] = None
            patched += 1

    if patched:
        with open(json_path, "w") as f:
            json.dump(case_data, f, indent=2)
        print(f"  Saved {patched} value_score entries to {os.path.basename(json_path)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = get_parser().parse_args()

    log_dir = args.log_dir or os.path.join(args.jsons_dir, "..", "logs_eval")
    log_dir = os.path.abspath(log_dir)
    os.makedirs(log_dir, exist_ok=True)

    json_files = sorted(
        glob(os.path.join(args.jsons_dir, "**", "*.json"),     recursive=True) +
        glob(os.path.join(args.jsons_dir, "**", "*.json.tmp"), recursive=True)
    )
    if not json_files:
        print(f"No JSON files found in {args.jsons_dir}")
        return

    # Prepare output CSV
    os.makedirs(os.path.dirname(os.path.abspath(args.output_csv)), exist_ok=True)
    out_f = open(args.output_csv, "w", newline="")
    writer = csv.DictWriter(out_f, fieldnames=OUTPUT_HEADER)
    writer.writeheader()

    for json_path in json_files:
        with open(json_path) as f:
            case_data = json.load(f)

        basename = os.path.basename(json_path)
        # Strip both .json and optional .tmp extension (e.g. "1_56.json.tmp" → "1_56")
        for ext in (".tmp", ".json"):
            if basename.endswith(ext):
                basename = basename[: -len(ext)]
        case_id = case_data.get("case", basename)
        print(f"Processing case: {case_id}")

        # Load ground truth once per case (reused across judges and pre-pass)
        df_gt = None
        try:
            df_gt = _load_gt(case_id, args.benchmark)
        except Exception as e:
            print(f"  Warning: could not load ground truth for {case_id}: {e}")

        active_judges = args.judges if args.judges else JUDGE_TYPES

        # Pre-pass: compute and cache value_score for any attempt that lacks it
        if "det_score_value" in active_judges and df_gt is not None:
            _patch_missing_value_scores(case_data, df_gt, case_id, args.benchmark, json_path)

        attempts = flatten_attempts(case_data)
        if not attempts:
            print(f"  No attempts found, skipping.")
            continue
        for judge_type in active_judges:
            logger = _make_logger(log_dir, case_id, judge_type)
            logger.info(f"=== Evaluating case {case_id} with judge {judge_type} ===")

            # Each judge type gets its own fresh LLM client/tracker so costs don't bleed
            tracker = TokenUsageTracker()
            llm_client = LLMClient(model=args.model, tracker=tracker, logger=logger)

            try:
                capped = [a for a in attempts if a["iteration"] <= args.max_iterations] if args.max_iterations else attempts
                result = simulate_judge(capped, judge_type, df_gt, llm_client, logger,
                                        case_id=case_id, benchmark=args.benchmark,
                                        score_source=args.score_source)
            except Exception as e:
                logger.error(f"Judge simulation failed: {e}", exc_info=True)
                result = {
                    "stopped_at": "error",
                    "stopped_correct": False,
                    "generation_cost": 0.0,
                    "generation_latency": 0.0,
                    "judge_cost": 0.0,
                    "judge_latency": 0.0,
                    "total_cost": 0.0,
                    "total_latency": 0.0,
                }

            row = {"case": case_id, "judge_type": judge_type, **result}
            writer.writerow(row)
            out_f.flush()
            print(f"  [{judge_type}] stopped_at={result['stopped_at']}, "
                  f"correct={result['stopped_correct']}, "
                  f"total_cost={result['total_cost']:.6f}")

    out_f.close()
    print(f"\nResults written to {args.output_csv}")


if __name__ == "__main__":
    main()
