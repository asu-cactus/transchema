"""Score run_openai_task.py results using the same "autopipeline" validation
Langraph/mcts_search.py uses via --validation autopipeline:
validation.hard_match.compare_tables_matching (wraps
validation/autopipeline_match.py's compare_tables).

This is a semantic, column-order-independent, value-set-based comparison --
it matches target columns to generated columns by content, not by requiring
identical column names/order. That's more forgiving than MMTU's own
TransformByTargetSchemaEvaluator, which requires literal columns==columns
equality. This script is additive: it does not touch evaluate.py or the
MMTU evaluator classes, so both scoring methods stay available side by side.

Usage:
    python3 evaluate_autopipeline.py mmtu.gpt-4-1-mini.result.jsonl
    python3 evaluate_autopipeline.py mmtu.gpt-4-1-mini.result.jsonl --length 1
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from validation.hard_match import compare_tables_matching

CODE_BLOCK_RE = re.compile(r"```python(.*?)```", re.DOTALL)


def extract_code(response):
    matches = CODE_BLOCK_RE.findall(response or "")
    if not matches:
        return None
    return matches[0].strip()


def parse_length(test_case):
    match = re.match(r"^length(\d+)_", test_case)
    return int(match.group(1)) if match else None


def _evaluate_row_star(args):
    return evaluate_row(*args)


def evaluate_row(row, data_root, exec_root, timeout):
    metadata = json.loads(row["metadata"])
    test_case = metadata["test_case"]
    case_dir = os.path.join(data_root, test_case)

    result = {"test_case": test_case, "length": parse_length(test_case), "is_correct": False, "reason": None, "error_detail": ""}

    code = extract_code(row.get("response", ""))
    if code is None:
        result["reason"] = "no_code_block"
        return result

    cur_exec_dir = os.path.join(exec_root, test_case)
    os.makedirs(cur_exec_dir, exist_ok=True)
    cur_dir = os.getcwd()
    try:
        os.chdir(cur_exec_dir)
        for entry in metadata.get("test", []):
            src = entry["data"]
            src_path = os.path.join(case_dir, src)
            assert os.path.exists(src_path), f"{src} missing in {case_dir}"
            # These CSVs carry a stray leading index column (the same column
            # MMTU's own prompt-builder drops via index_col=0 when rendering
            # sample rows). The LLM never sees it in the prompt, so strip it
            # here too -- otherwise it resurfaces as a literal "Unnamed: 0"
            # column and collides across merges of 3+ source tables.
            df_src = pd.read_csv(src_path, index_col=0)
            df_src.to_csv(src.replace("test_", "source_"), index=False)

        with open("transform.py", "w") as f:
            f.write(code)

        try:
            proc = subprocess.run(["python3", "transform.py"], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            result["reason"] = "exec_timeout"
            return result

        if proc.returncode != 0:
            result["reason"] = "exec_error"
            result["error_detail"] = proc.stderr.strip()[-500:]
            return result

        if not os.path.exists("output.csv"):
            result["reason"] = "no_output_file"
            return result

        df_output = pd.read_csv("output.csv", low_memory=False)
        df_gt = pd.read_csv(os.path.join(case_dir, "target.csv"), low_memory=False)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        try:
            _, is_correct, _, _ = compare_tables_matching(df_output, df_gt)
            result["is_correct"] = bool(is_correct)
            result["reason"] = "scored"
        except Exception as e:
            result["reason"] = "compare_exception"
            result["error_detail"] = str(e)
    except Exception as e:
        result["reason"] = "sandbox_error"
        result["error_detail"] = str(e)
    finally:
        os.chdir(cur_dir)

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("result_file", help="Result jsonl produced by run_openai_task.py")
    parser.add_argument("--data_root", default=os.path.join(REPO_ROOT, "autopipeline-benchmarks", "github-pipelines"))
    parser.add_argument("--length", type=int, default=None, help="Only evaluate rows for this length bucket")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel worker processes (each case runs in its own sandbox dir, safe to parallelize)")
    parser.add_argument("--output_dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "autopipeline_eval_results"))
    args = parser.parse_args()

    rows = []
    with open(args.result_file) as f:
        for line in f:
            row = json.loads(line)
            if args.length is not None:
                metadata = json.loads(row["metadata"])
                if parse_length(metadata.get("test_case", "")) != args.length:
                    continue
            rows.append(row)

    assert rows, "No rows to evaluate (check --length / result_file)"
    print(f"Evaluating {len(rows)} rows with autopipeline validation (compare_tables_matching)")

    os.makedirs(args.output_dir, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    exec_root = os.path.join(REPO_ROOT, "MMTU", "tmp_exec", f"autopipeline_eval_{now}")
    os.makedirs(exec_root, exist_ok=True)

    job_args = [(row, args.data_root, exec_root, args.timeout) for row in rows]
    if args.workers == 1:
        results = [evaluate_row(*a) for a in tqdm(job_args, desc="Evaluating", ncols=100)]
    else:
        with Pool(args.workers) as pool:
            results = list(tqdm(pool.imap(_evaluate_row_star, job_args), total=len(job_args), desc="Evaluating", ncols=100))
    df = pd.DataFrame(results)

    model_tag = rows[0].get("model_name", "unknown").replace(".", "-")
    details_path = os.path.join(args.output_dir, f"{model_tag}_details.csv")
    df.to_csv(details_path, index=False)

    summary_rows = []
    for length, group in sorted(df.groupby("length"), key=lambda kv: kv[0]):
        n = len(group)
        n_correct = int(group["is_correct"].sum())
        summary_rows.append({"length": length, "n": n, "n_correct": n_correct, "acc": n_correct / n})
    overall_n = len(df)
    overall_correct = int(df["is_correct"].sum())
    summary_rows.append({"length": "overall", "n": overall_n, "n_correct": overall_correct, "acc": overall_correct / overall_n})
    summary_df = pd.DataFrame(summary_rows)
    summary_path = os.path.join(args.output_dir, f"{model_tag}_summary.csv")
    summary_df.to_csv(summary_path, index=False)

    print()
    print(summary_df.to_string(index=False))
    print()
    print("Reason breakdown:")
    print(df["reason"].value_counts().to_string())
    print()
    print(f"Details: {details_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
