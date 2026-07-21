import argparse
import csv
import json
import logging
import os
import time
from datetime import datetime

import pandas as pd

from util import create_connection, execute_sql
from join_util import (
    convert_target_names,
    num_source_tables,
    clean_source_csv_path,
    read_target_dataframe,
)
from gpt import chat_with_gpt, DEFAULT_MODEL
from join import validation
from autopipeline_validation import validate_autopipeline_style
from cost import estimate_cost

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGS_ROOT = os.path.join(_THIS_DIR, "logs")

VALIDATION_METHODS = {
    "inbuilt": "join",  # join.py's validation(), unchanged
    "join": "join",
    "hard_match": "hard_match",
    "autopipeline": "autopipeline",
}


def setup_experiment(experiment_name):
    """Create logs/{experiment_name}_{timestamp}/ and point logging at a run.log
    inside it. Returns the experiment directory path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = os.path.join(_LOGS_ROOT, f"{experiment_name}_{timestamp}")
    os.makedirs(experiment_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)
    handler = logging.FileHandler(os.path.join(experiment_dir, "run.log"))
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(handler)

    return experiment_dir


def load_case_records(json_paths):
    """Load the (flat-list) benchmark JSON files and group rows by Target Data Name.

    Each row is one (target, source) pair; a case with N source tables has N rows
    sharing the same "Target Data Name". Sources within a case are ordered by the
    numeric suffix of "Source Data Name" (e.g. Source6_56_0, Source6_56_1, ...).
    """
    records = []
    for path in json_paths:
        with open(path) as f:
            records.extend(json.load(f))

    by_target = {}
    for r in records:
        by_target.setdefault(r["Target Data Name"], []).append(r)
    for group in by_target.values():
        group.sort(key=lambda r: int(r["Source Data Name"].rsplit("_", 1)[1]))
    return by_target


def generate_prompt_auto_pipeline(records, target_name, source_paths):
    """Build a prompt for a case with an arbitrary number of source tables.

    `records` are this case's rows (one per source table, sharing Target Data Name).
    `source_paths` are index-column-stripped, full (not sampled) CSV paths, one per
    source, aligned to `records` order — these are what the generated SQL's COPY
    statements should load, while the schema/sample text shown to the model comes
    from the JSON (small samples only, not the full data).
    """
    target_schema = records[0]["Target Data Schema with Types"]
    target_sample = records[0]["Target Data Sample"]

    source_blocks = []
    for i, (rec, path) in enumerate(zip(records, source_paths)):
        source_blocks.append(f"""Source table {i} (name: {rec['Source Data Name']}):
  Schema: {rec['Source Data Schema with Types']}
  Sample rows: {rec['3 Samples of Source Data']}
  Full data file to load (has a header row; the row-index column has already been removed): {path}""")
    sources_text = "\n\n".join(source_blocks)

    return f"""You are a SQL developer. Please generate a Postgres SQL script that produces a target table
by transforming and/or joining {len(records)} source table(s) so that it matches the given target schema,
using the sample rows below only as a hint of the required transformation logic.

{sources_text}

Target table (name: {target_name}):
  Schema: {target_schema}
  A few example output rows (illustration only, not the full expected result): {target_sample}

Please follow these steps:
1. For each source table above: drop it if it exists, CREATE TABLE with exactly the given schema and types,
   then load the FULL data with:
   COPY <source_table_name> FROM '<its full data file path>' WITH (FORMAT csv, HEADER true, NULL '');
2. Drop the target table {target_name} if it exists, then CREATE TABLE {target_name} with only the given target schema/types.
3. Write and execute an INSERT INTO {target_name} SELECT ... query that transforms/joins the source table(s)
   into the target table's shape.
4. Don't remove any of the tables, we need them for validation.
5. Please quote the entire returned SQL script between "```sql\n" and "\n```".
"""


def run_case(conn, target_name, records, model=DEFAULT_MODEL, max_tokens=12000, validation_method="join"):
    """Run and validate one benchmark case end-to-end. Never raises — failures are
    reported in the returned dict so a batch run can continue past a bad case.

    validation_method:
      - "join" (default): join.py's validation() — unchanged, positional column
        comparison, sorted rows. This is the method used throughout this file so far.
      - "hard_match" / "autopipeline": the same compare_lists_matching /
        compare_tables_matching used by Langraph/mcts_search.py to score the
        MCTS/pandas pipeline, for an apples-to-apples comparison against that system.

    Returns (result, record) where `result` is the compact per-case summary (goes in
    results.csv) and `record` carries the full prompt/response text (goes in
    prompts_responses.jsonl) — kept separate so the CSV stays readable.
    """
    case_name = convert_target_names(target_name)
    n_sources = len(records)
    case_start = time.time()

    on_disk = num_source_tables(case_name)
    if on_disk != n_sources:
        logging.warning(f"{target_name}: JSON has {n_sources} source(s) but {case_name} has {on_disk} test_*.csv on disk")

    result = {"target": target_name, "case": case_name, "n_sources": n_sources,
              "model": model, "validation_method": validation_method,
              "accuracy": 0.0, "correct": False, "detail": None, "error": None,
              "prompt_tokens": None, "completion_tokens": None, "cost_usd": None,
              "llm_latency_seconds": None, "total_latency_seconds": None}
    record = {"target": target_name, "model": model, "prompt": None, "response": None,
              "usage": None, "llm_latency_seconds": None}
    try:
        source_paths = [clean_source_csv_path(case_name, i) for i in range(n_sources)]
        prompt = generate_prompt_auto_pipeline(records, target_name, source_paths)
        record["prompt"] = prompt
        logging.info(f"{target_name}: prompt built ({len(prompt)} chars)")

        gpt_output, usage, llm_latency = chat_with_gpt(
            prompt, max_tokens=max_tokens, model=model, return_usage=True)
        record["response"] = gpt_output
        record["usage"] = usage
        record["llm_latency_seconds"] = llm_latency
        result["prompt_tokens"] = usage.get("prompt_tokens")
        result["completion_tokens"] = usage.get("completion_tokens")
        result["cost_usd"] = estimate_cost(model, usage)
        result["llm_latency_seconds"] = llm_latency
        logging.info(f"{target_name}: gpt sql ({llm_latency:.2f}s, usage={usage}):\n{gpt_output}")

        sql_result = execute_sql(conn, gpt_output)
        if isinstance(sql_result, str) and sql_result.startswith("Error:"):
            result["error"] = sql_result
            return result, record

        # execute_sql()'s own auto-detected "target table" (util.py's
        # extract_target_table_name) assumes at most 2 source tables — it picks
        # the 3rd CREATE TABLE statement seen, which is wrong for cases with more
        # sources. We already know the exact target table name from the JSON, so
        # query it directly instead of trusting that guess (also gives us real
        # column names, needed for the name-based hard_match method below).
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {target_name};")
        sql_rows = cur.fetchall()
        sql_cols = [d[0] for d in cur.description]
        sql_result_df = pd.DataFrame(sql_rows, columns=sql_cols)
        target_df = read_target_dataframe(case_name)

        if validation_method == "join":
            if len(sql_result_df.columns) != len(target_df.columns):
                result["error"] = (f"Column count mismatch: got {len(sql_result_df.columns)}, "
                                    f"expected {len(target_df.columns)}")
                return result, record
            # Align on sorted rows (both DataFrames) so row-order differences between
            # the generated SQL and the reference pipeline don't register as mismatches.
            sql_result_df = sql_result_df.sort_values(by=list(sql_result_df.columns)).reset_index(drop=True)
            target_df = target_df.sort_values(by=list(target_df.columns)).reset_index(drop=True)
            case_accuracy, is_correct, similarity_scores, detail = validation(sql_result_df, target_df)
        else:
            case_accuracy, is_correct, similarity_scores, detail = validate_autopipeline_style(
                sql_result_df, target_df, method=validation_method)

        result["accuracy"] = case_accuracy
        result["correct"] = is_correct
        result["detail"] = detail or None
        logging.info(f"{target_name}: accuracy={case_accuracy}, correct={is_correct}")
    except Exception as e:
        logging.exception(f"{target_name}: failed")
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        result["total_latency_seconds"] = time.time() - case_start
    return result, record


def run_many(by_target, target_names, model=DEFAULT_MODEL, max_tokens=12000,
             validation_method="join", experiment_dir=None):
    if experiment_dir is None:
        experiment_dir = setup_experiment("adhoc")
    os.makedirs(experiment_dir, exist_ok=True)

    conn = create_connection()
    results = []
    records_path = os.path.join(experiment_dir, "prompts_responses.jsonl")
    results_path = os.path.join(experiment_dir, "results.csv")
    csv_writer = None
    try:
        with open(records_path, "w") as records_file, open(results_path, "w", newline="") as results_file:
            for i, target_name in enumerate(target_names):
                print(f"[{i + 1}/{len(target_names)}] {target_name}")
                if target_name not in by_target:
                    print(f"  -> skipped: not found in loaded JSON records")
                    logging.warning(f"{target_name}: not found in loaded JSON records, skipping")
                    continue
                records = by_target[target_name]
                res, record = run_case(conn, target_name, records, model=model, max_tokens=max_tokens,
                                        validation_method=validation_method)
                print(f"  -> accuracy={res['accuracy']:.2f} correct={res['correct']} "
                      f"cost=${res['cost_usd'] if res['cost_usd'] is not None else 'n/a'} "
                      f"latency={res['total_latency_seconds']:.1f}s "
                      f"error={res['error']} detail={res['detail']}")
                results.append(res)

                # Write each result/record as soon as it's ready (not just at the
                # end) so a crash or interruption partway through a batch doesn't
                # lose already-completed cases.
                if csv_writer is None:
                    csv_writer = csv.DictWriter(results_file, fieldnames=list(res.keys()))
                    csv_writer.writeheader()
                csv_writer.writerow(res)
                results_file.flush()
                os.fsync(results_file.fileno())

                records_file.write(json.dumps(record) + "\n")
                records_file.flush()
                os.fsync(records_file.fileno())
    finally:
        conn.close()

    df = pd.DataFrame(results)
    n_correct = int(df['correct'].sum()) if len(df) else 0
    total_cost = df['cost_usd'].dropna().sum() if len(df) else 0.0
    total_latency = df['total_latency_seconds'].dropna().sum() if len(df) else 0.0
    print(f"\n{n_correct}/{len(df)} correct. Total cost ~${total_cost:.4f}, "
          f"total latency {total_latency:.1f}s.")
    print(f"Results: {results_path}")
    print(f"Prompts/responses: {records_path}")
    print(f"Log: {os.path.join(experiment_dir, 'run.log')}")
    return df


def _build_target_names(len_id, start_id, end_id):
    return [f"Target{len_id}_{i}" for i in range(start_id, end_id + 1)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the SQL-generation baseline over a range of "
                                                   "AutoPipeline github-pipelines benchmark cases.")
    parser.add_argument("--len", type=int, required=True, dest="len_id",
                        help="Length group (the N in lengthN_M / TargetN_M), e.g. 1")
    parser.add_argument("--start_target_id", type=int, required=True,
                        help="First case index (inclusive)")
    parser.add_argument("--end_target_id", type=int, required=True,
                        help="Last case index (inclusive)")
    parser.add_argument("--validation", choices=sorted(VALIDATION_METHODS), default="inbuilt",
                        help="'inbuilt' = join.py's validation() (default); 'hard_match'/'autopipeline' = "
                             "the same methods Langraph/mcts_search.py uses, for comparability")
    parser.add_argument("--experiment_name", type=str, required=True,
                        help="Logs/results go to logs/{experiment_name}_{timestamp}/")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--max_tokens", type=int, default=12000)
    args = parser.parse_args()

    experiment_dir = setup_experiment(args.experiment_name)
    print(f"Experiment dir: {experiment_dir}")

    by_target = load_case_records([
        os.path.join(_THIS_DIR, "..", "data", "chatgpt_github_ss.json"),
        os.path.join(_THIS_DIR, "..", "data", "chatgpt_github_ms.json"),
    ])
    target_names = _build_target_names(args.len_id, args.start_target_id, args.end_target_id)
    print(f"Running {len(target_names)} case(s): {target_names[0]}..{target_names[-1]}")

    run_many(by_target, target_names, model=args.model, max_tokens=args.max_tokens,
             validation_method=VALIDATION_METHODS[args.validation], experiment_dir=experiment_dir)
