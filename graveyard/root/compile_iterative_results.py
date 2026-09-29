"""
compile_iterative_results.py

Reads iterative experiment JSON files and computes aggregated results
using only the FIRST iteration of each case:

  ms / sscot              — iter 1 MS attempt only
  ms_critique / sscot_critique — iter 1 MS + all iter 1 critiques combined
    - is_correct : True if MS OR any critique was correct
    - score      : best score across MS + critiques
    - cost       : sum of MS cost + all critique costs
    - latency    : sum of MS latency + all critique latencies

Outputs:
  --output_csv   : one row per (label, method) with aggregated metrics
  --percase_csv  : one row per (label, method, case) with raw metrics

Usage:
  python3 compile_iterative_results.py \
      --output_csv results/compiled_summary.csv \
      --percase_csv results/compiled_percase.csv
"""

import json
import os
import glob
import csv
import argparse


# ---------------------------------------------------------------------------
# Experiment registry
# Each entry: (label, method_base, [list of jsons/ directories])
# ---------------------------------------------------------------------------
EXPERIMENTS = [
    # GitHub — Multi-step
    ("github_l1", "ms",    ["logs-auto-suggest-llm-21-04/len_1_iterative_implementation_10_iter_20260413_002538/jsons"]),
    ("github_l4", "ms",    ["logs-auto-suggest-llm-21-04/len_4_iterative_10_iter_20260415_184739/jsons"]),
    ("github_l9", "ms",    [
        "logs-auto-suggest-llm-21-04/len_9_iterative_10_iter_b1_20260417_125443/jsons",
        "logs-auto-suggest-llm-21-04/len_9_iterative_10_iter_b2_20260417_125501/jsons",
        "logs-auto-suggest-llm-21-04/len_9_iterative_10_iter_b3_20260417_125534/jsons",
    ]),

    # GitHub — SSCoT
    ("github_l1", "sscot", ["logs-auto-suggest-llm-21-04/github_l1_sscot_iterative_10_20260419_194334/jsons"]),
    ("github_l4", "sscot", ["logs-auto-suggest-llm-21-04/github_l4_sscot_iterative_10_20260419_194334/jsons"]),
    ("github_l9", "sscot", ["logs-auto-suggest-llm-21-04/github_l9_sscot_iterative_10_20260419_194334/jsons"]),

    # Monteprep — Multi-step
    ("monteprep_l1", "ms", ["logs-auto-suggest-llm-21-04/monteprep_l1_iterative_10_20260417_163444/jsons"]),
    ("monteprep_l4", "ms", ["logs-auto-suggest-llm-21-04/monteprep_l4_iterative_10_20260417_191536/jsons"]),
    ("monteprep_l9", "ms", ["logs-auto-suggest-llm-21-04/monteprep_l9_iterative_10_20260417_232148/jsons"]),

    # Monteprep — SSCoT
    ("monteprep_l1", "sscot", ["logs-auto-suggest-llm-21-04/monteprep_l1_sscot_iterative_10_20260419_194501/jsons"]),
    ("monteprep_l4", "sscot", ["logs-auto-suggest-llm-21-04/monteprep_l4_sscot_iterative_10_20260419_194501/jsons"]),
    ("monteprep_l9", "sscot", ["logs-auto-suggest-llm-21-04/monteprep_l9_sscot_iterative_10_20260419_194501/jsons"]),
]

SUMMARY_HEADER = ["label", "method", "n_cases", "n_correct", "avg_score", "avg_cost", "avg_latency"]
PERCASE_HEADER = ["label", "method", "case", "is_correct", "score", "cost", "latency"]


def load_jsons(jsons_dirs):
    """Load all JSONs from a list of directories, deduplicating by case id."""
    seen = {}
    for d in jsons_dirs:
        for path in sorted(glob.glob(os.path.join(d, "*.json"))):
            with open(path) as f:
                data = json.load(f)
            case = data.get("case", os.path.splitext(os.path.basename(path))[0])
            if case not in seen:
                seen[case] = data
    return list(seen.values())


def extract_iter1(case_data):
    iterations = case_data.get("iterations", [])
    if not iterations:
        return None, []
    iter1 = iterations[0]
    return iter1.get("ms", {}), iter1.get("critiques", [])


def ms_result(ms):
    return {
        "is_correct": bool(ms.get("is_correct", False)),
        "score":      float(ms.get("score", 0.0)),
        "cost":       float(ms.get("cost", 0.0)),
        "latency":    float(ms.get("latency", 0.0)),
    }


def ms_crit_result(ms, critiques):
    is_correct = bool(ms.get("is_correct", False))
    score      = float(ms.get("score", 0.0))
    cost       = float(ms.get("cost", 0.0))
    latency    = float(ms.get("latency", 0.0))
    for c in critiques:
        is_correct = is_correct or bool(c.get("is_correct", False))
        score      = max(score, float(c.get("score", 0.0)))
        cost      += float(c.get("cost", 0.0))
        latency   += float(c.get("latency", 0.0))
    return {"is_correct": is_correct, "score": score, "cost": cost, "latency": latency}


def aggregate(records):
    n = len(records)
    if n == 0:
        return {"n_cases": 0, "n_correct": 0, "avg_score": 0.0, "avg_cost": 0.0, "avg_latency": 0.0}
    return {
        "n_cases":     n,
        "n_correct":   sum(1 for r in records if r["is_correct"]),
        "avg_score":   round(sum(r["score"]   for r in records) / n, 4),
        "avg_cost":    round(sum(r["cost"]     for r in records) / n, 6),
        "avg_latency": round(sum(r["latency"]  for r in records) / n, 4),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_csv",  default="results/compiled_summary.csv")
    parser.add_argument("--percase_csv", default="results/compiled_percase.csv")
    args = parser.parse_args()

    for path in [args.output_csv, args.percase_csv]:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    summary_rows = []
    percase_rows = []

    for label, method_base, jsons_dirs in EXPERIMENTS:
        cases = load_jsons(jsons_dirs)
        if not cases:
            print(f"WARNING: no JSONs for {label} {method_base}")
            continue

        alone_records = []
        crit_records  = []

        for case_data in cases:
            case_id = case_data.get("case", "?")
            ms, critiques = extract_iter1(case_data)
            if ms is None:
                continue

            r_alone = ms_result(ms)
            r_crit  = ms_crit_result(ms, critiques)

            alone_records.append(r_alone)
            crit_records.append(r_crit)

            m_alone = method_base
            m_crit  = f"{method_base}_critique"
            percase_rows.append([label, m_alone, case_id, r_alone["is_correct"], r_alone["score"], r_alone["cost"], r_alone["latency"]])
            percase_rows.append([label, m_crit,  case_id, r_crit["is_correct"],  r_crit["score"],  r_crit["cost"],  r_crit["latency"]])

        m_alone = method_base
        m_crit  = f"{method_base}_critique"
        agg_alone = aggregate(alone_records)
        agg_crit  = aggregate(crit_records)

        summary_rows.append([label, m_alone, agg_alone["n_cases"], agg_alone["n_correct"], agg_alone["avg_score"], agg_alone["avg_cost"], agg_alone["avg_latency"]])
        summary_rows.append([label, m_crit,  agg_crit["n_cases"],  agg_crit["n_correct"],  agg_crit["avg_score"],  agg_crit["avg_cost"],  agg_crit["avg_latency"]])

        print(f"{label:20s}  {m_alone:20s}  n={agg_alone['n_cases']:3d}  correct={agg_alone['n_correct']:3d}  score={agg_alone['avg_score']:.3f}  cost={agg_alone['avg_cost']:.5f}  lat={agg_alone['avg_latency']:.1f}s")
        print(f"{label:20s}  {m_crit:20s}  n={agg_crit['n_cases']:3d}  correct={agg_crit['n_correct']:3d}  score={agg_crit['avg_score']:.3f}  cost={agg_crit['avg_cost']:.5f}  lat={agg_crit['avg_latency']:.1f}s")

    with open(args.output_csv, "w", newline="") as f:
        csv.writer(f).writerows([SUMMARY_HEADER] + summary_rows)

    with open(args.percase_csv, "w", newline="") as f:
        csv.writer(f).writerows([PERCASE_HEADER] + percase_rows)

    print(f"\nSummary  → {args.output_csv}")
    print(f"Per-case → {args.percase_csv}")


if __name__ == "__main__":
    main()
