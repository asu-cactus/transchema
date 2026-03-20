"""
Script to process data transformation cases and log results.
Cases are determined by (len_id, target_id) ranges using get_test_cases_ids.
Queries are generated dynamically via get_prompt(prompt_type="get_case_info").
"""

import argparse
import csv
import os
import sys
import json
import traceback
import multiprocessing
from datetime import datetime

# Ensure the transchema root is on the path so shared utilities are importable.
_TRANSCHEMA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)

from agentflow.agentflow.solver import construct_solver, setup_logging
from agentflow.engine.engine_utils import TOKEN_TRACKER
from test_scope import get_test_cases_ids
from util.utils import get_test_info
from auto_suggest_llm_util import get_prompt

# ============================================================
# CLI Arguments
# ============================================================
_parser = argparse.ArgumentParser(description="Run AgentFlow data transformation cases.")
_parser.add_argument("--len-id", type=int, default=1,
                     help="Length ID for the test cases (default: 1)")
_parser.add_argument("--max-len-id", type=int, default=1,
                     help="Maximum length ID for range mode (default: 1)")
_parser.add_argument("--target-id-start", type=int, default=0,
                     help="Start of target ID range, inclusive (default: 0)")
_parser.add_argument("--target-id-end", type=int, default=10,
                     help="End of target ID range, inclusive (default: 10)")
_parser.add_argument("--llm-engine", type=str, default="gpt-4.1-mini",
                     help="LLM engine name (default: gpt-4.1-mini)")
_parser.add_argument("--planner-granularity", type=str, default="operator",
                     choices=["operator", "pipeline"],
                     help="Planner granularity: 'operator' or 'pipeline' (default: operator)")
_parser.add_argument("--execute-pipeline", action=argparse.BooleanOptionalAction,
                     default=True,
                     help="Enable/disable pipeline execution and scoring in the agentic loop (default: True)")
_parser.add_argument("--result-dir", type=str, default="run",
                     help="Base name for the results directory under AgentFlow/results/ (a timestamp is appended)")
_parser.add_argument("--validation", type=str, default="hard_match",
                     choices=["hard_match", "autopipeline"],
                     help="Validation method: 'hard_match' uses compare_lists_matching (partial credit), 'autopipeline' uses compare_tables_matching (binary match) (default: hard_match)")
_parser.add_argument("--cases", type=str, nargs="+", default=None,
                     help="Explicit list of case IDs to run, e.g. --cases 1_41 4_18 9_70. "
                          "Overrides --len-id / --target-id-start / --target-id-end.")
_parser.add_argument("--benchmark", type=str, default="github",
                     choices=["github", "monteprep"],
                     help="Benchmark dataset: 'github' or 'monteprep'. (default: github)")
_args = _parser.parse_args()

# ============================================================
# CASE CONFIGURATION
# ============================================================
# Option A — Explicit list of target IDs (for case-based testing):
#   Set TARGET_IDS to a list, e.g. [4, 6, 48, 56]
#
# Option B — Range of target IDs (for mass testing):
#   Set TARGET_IDS to None and configure the range below.
#
LEN_ID = _args.len_id
TARGET_IDS = None  # None  # [13]
# 16, 17, 18, 19,
# 20, 21, 22, 23, 24, 25,
# 27,
# 28,
# 29,
# 32, 33,
# 36,
# 38,
# 40, 41, 42, 43,
# 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
# 59, 60, 61,
# 68,
# 70, 71,
# 75,
# 77, 78,
# 81,
# 84,
# 92, 93, 94, 95, 96,
# 100,
# ]  # e.g. [4, 6, 48, 56] or None for range mode

# Range mode settings (only used when TARGET_IDS is None)
MAX_LEN_ID = _args.max_len_id
TARGET_ID_START = _args.target_id_start
TARGET_ID_END = _args.target_id_end
# ============================================================

# Paths
_BENCHMARK = _args.benchmark
if _BENCHMARK == "monteprep":
    JSON_FILE_PATH_MS = os.path.join(_TRANSCHEMA_ROOT, "data", "chatgpt_monteprep_ms.json")
    JSON_FILE_PATH_SS = os.path.join(_TRANSCHEMA_ROOT, "data", "chatgpt_monteprep_ss.json")
    BENCHMARKS_DIR = os.path.join(
        _TRANSCHEMA_ROOT, "autopipeline-benchmarks", "monteprep-pipelines"
    )
else:
    JSON_FILE_PATH_MS = os.path.join(_TRANSCHEMA_ROOT, "data", "chatgpt_github_ms.json")
    JSON_FILE_PATH_SS = os.path.join(_TRANSCHEMA_ROOT, "data", "chatgpt_github_ss.json")
    BENCHMARKS_DIR = os.path.join(
        _TRANSCHEMA_ROOT, "autopipeline-benchmarks", "github-pipelines"
    )
_RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS_DIR = os.path.join(
    _TRANSCHEMA_ROOT, "AgentFlow", "results", f"{_args.result_dir}_{_RUN_TIMESTAMP}"
)

# Model / solver configuration
LLM_ENGINE_NAME = _args.llm_engine

# Planner granularity:
#   "operator" = operator-level planning
#   "pipeline" = pipeline-level planning
PLANNER_GRANULARITY = _args.planner_granularity

# Pipeline execution + scoring inside the agentic loop
EXECUTE_PIPELINE = _args.execute_pipeline

# Validation method: "hard_match" or "autopipeline"
VALIDATION = _args.validation

# Start Again Tool behavior
START_AGAIN_CLEAR_HISTORY = False

# ============================================================
# Derive the list of cases
# ============================================================
if _args.cases:
    # Option C: explicit case IDs via --cases (overrides everything else)
    CASES_TO_RUN = _args.cases
elif TARGET_IDS is not None:
    # Option A: explicit list hardcoded in script
    CASES_TO_RUN = [f"{LEN_ID}_{tid}" for tid in TARGET_IDS]
else:
    # Option B: range via get_test_cases_ids (both MS and SS)
    task_list_ms = get_test_cases_ids(
        JSON_FILE_PATH_MS, LEN_ID, MAX_LEN_ID, TARGET_ID_START, TARGET_ID_END
    )
    task_list_ss = get_test_cases_ids(
        JSON_FILE_PATH_SS, LEN_ID, MAX_LEN_ID, TARGET_ID_START, TARGET_ID_END
    )
    CASES_TO_RUN = sorted(set(t[6:] for t in task_list_ms + task_list_ss))

os.makedirs(RESULTS_DIR, exist_ok=True)

print(f"Cases selected to run: {CASES_TO_RUN}\n")

# ============================================================
# Results CSV — written incrementally after each case
# ============================================================
RESULTS_CSV_PATH = os.path.join(RESULTS_DIR, "results_summary.csv")
_CSV_FIELDS = [
    "case_id",
    "status",
    "is_correct",
    "score",
    "score_fd",
    "column_mapping_score",
    "average_similarity",
    "latency_seconds",
    "cost",
    "timestamp",
    "error",
]

with open(RESULTS_CSV_PATH, "w", newline="") as _f:
    csv.DictWriter(_f, fieldnames=_CSV_FIELDS).writeheader()

_CASE_TIMEOUT = 600  # 10 minutes per case


def _af_case_worker(
    case_id, results_dir, results_csv_path, csv_fields,
    benchmarks_dir, json_ms, json_ss,
    llm_engine, planner_granularity, execute_pipeline,
    validation, start_again_clear_history,
    transchema_root, result_queue,
):
    """Runs one AgentFlow case fully in a child process."""
    if transchema_root not in sys.path:
        sys.path.insert(0, transchema_root)

    case_results_dir = os.path.join(results_dir, f"case_{case_id}")
    case_logs_dir = os.path.join(case_results_dir, "logs")
    os.makedirs(case_logs_dir, exist_ok=True)
    TOKEN_TRACKER.reset()

    try:
        logger, component_loggers = setup_logging(case_logs_dir)

        import agentflow.agentflow.solver as solver_module
        solver_module.logger = logger
        solver_module.prompt_logger = component_loggers["prompts"]
        solver_module.tool_logger = component_loggers["tools"]
        solver_module.memory_logger = component_loggers["memory"]

        path_to_files = os.path.join(benchmarks_dir, f"length{case_id}")
        file_count = sum(
            1 for _, _, files in os.walk(path_to_files)
            for file in files if file.startswith("test")
        )
        json_file_path = json_ms if file_count > 1 else json_ss

        (
            target_data_name,
            target_data_schema,
            target_data_schema_with_types,
            _target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            _source_samples_list,
        ) = get_test_info(json_file_path, case_id, benchmarks_dir, anon_flag=0)

        query = get_prompt(
            prompt_type="get_case_info",
            allowed_operation_list=[],
            operation_history=[],
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples="",
            file_count=file_count,
            directory=benchmarks_dir,
            len_idx_target_idx=case_id,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            target_data_schema_with_types=target_data_schema_with_types,
            target_length=3,
            source_length=3,
            model=llm_engine,
        )

        print(f"Query generated ({len(query)} characters)")

        if planner_granularity == "pipeline":
            enabled_tools = [
                "Create_New_Pipeline",
                "Refine_Existing_Pipeline",
                "Code_Generator_Tool",
                "Finalize_Pipeline_Tool",
            ]
        else:
            enabled_tools = [
                "Configure_Join_Operator_Tool",
                "Configure_Union_Operator_Tool",
                "Configure_GroupBy_Aggregate_Operator_Tool",
                "Add_Pivot_Tool",
                "Add_Unpivot_Tool",
                "Code_Gen_And_Score_Tool",
                "Critique_Pipeline_Tool",
            ]
        tool_engine = ["Default"] * len(enabled_tools)

        ground_truth_csv = os.path.join(benchmarks_dir, f"length{case_id}", "target.csv")
        if not os.path.isfile(ground_truth_csv):
            print(f"WARNING: Ground truth not found at {ground_truth_csv}")
            ground_truth_csv = None

        solver = construct_solver(
            llm_engine_name=llm_engine,
            enabled_tools=enabled_tools,
            tool_engine=tool_engine,
            model_engine=["trainable", "trainable", "trainable", "trainable"],
            start_again_clear_history=start_again_clear_history,
            planner_granularity=planner_granularity,
            execute_pipeline=execute_pipeline,
            ground_truth_csv=ground_truth_csv,
            validation=validation,
        )

        print(f"Starting solver...")
        start_time = datetime.now()
        output = solver.solve(query)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        is_correct = output.get("is_correct", False)
        case_status = "correct" if is_correct else "incorrect"
        status_icon = "✓" if is_correct else "✗"
        print(f"\n{status_icon} Case {case_id} completed in {duration:.2f}s — {case_status.upper()}")

        result_file = os.path.join(case_results_dir, f"{case_id}_result.txt")
        with open(result_file, "w") as f:
            f.write(f"Case: {case_id}\n")
            f.write(f"Status: {case_status.upper()}\n")
            f.write(f"Timestamp: {start_time.isoformat()}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"LLM Engine: {llm_engine}\n")
            f.write(f"Logs Directory: {case_logs_dir}\n")
            verification = output.get("verification_result", {})
            if verification:
                f.write(f"\nVerification:\n")
                f.write(f"  is_correct: {is_correct}\n")
                f.write(f"  average_similarity: {verification.get('average_similarity', 'N/A')}\n")
                f.write(f"  matched_columns: {verification.get('all_matched_columns', [])}\n")
                f.write(f"  calculate_score: {verification.get('calculate_score', 'N/A')}\n")
            f.write(f"\n{'='*80}\nQUERY:\n{'='*80}\n")
            f.write(query)
            f.write(f"\n\n{'='*80}\nOUTPUT:\n{'='*80}\n")
            f.write(str(output.get("direct_output", output.get("final_output", "No output"))))

        json_output_file = os.path.join(case_results_dir, f"{case_id}_full_output.json")
        with open(json_output_file, "w") as f:
            json.dump(output, f, indent=2, default=str)

        print(f"{status_icon} Result saved to: {result_file}")
        print(f"{status_icon} Full output saved to: {json_output_file}")

        final_score = output.get("final_score") or {}
        verification = output.get("verification_result") or {}
        _token_totals = TOKEN_TRACKER.get_totals()
        _cost = TOKEN_TRACKER.compute_cost(llm_engine)
        _csv_row = {
            "case_id": case_id,
            "status": case_status,
            "is_correct": is_correct,
            "score": final_score.get("score"),
            "score_fd": final_score.get("score_fd"),
            "column_mapping_score": final_score.get("column_mapping_score"),
            "average_similarity": verification.get("average_similarity"),
            "latency_seconds": round(duration, 2),
            "cost": round(_cost, 6) if _cost is not None else "N/A",
            "timestamp": start_time.isoformat(),
            "error": "",
        }
        with open(results_csv_path, "a", newline="") as _f:
            csv.DictWriter(_f, fieldnames=csv_fields).writerow(_csv_row)
        print(
            f"{status_icon} Tokens — prompt: {_token_totals['prompt_tokens']}, "
            f"completion: {_token_totals['completion_tokens']}, calls: {_token_totals['num_calls']} "
            f"| Cost: ${_cost:.6f}" if _cost is not None
            else f"{status_icon} Tokens — {_token_totals} | Cost: N/A"
        )

        result_queue.put(("ok", {
            "case": case_id,
            "status": case_status,
            "is_correct": is_correct,
            "duration_seconds": duration,
            "timestamp": start_time.isoformat(),
            "result_file": result_file,
            "json_output_file": json_output_file,
            "logs_directory": case_logs_dir,
        }))

    except Exception:
        error_tb = traceback.format_exc()
        print(f"\n✗ Error processing case {case_id}:\n{error_tb}")

        error_file = os.path.join(case_results_dir, f"{case_id}_error.txt")
        with open(error_file, "w") as f:
            f.write(f"Case: {case_id}\nTimestamp: {datetime.now().isoformat()}\n\n{error_tb}\n")

        _cost = TOKEN_TRACKER.compute_cost(llm_engine)
        _csv_row = {
            "case_id": case_id,
            "status": "error",
            "is_correct": False,
            "score": None,
            "score_fd": None,
            "column_mapping_score": None,
            "average_similarity": None,
            "latency_seconds": None,
            "cost": round(_cost, 6) if _cost is not None else "N/A",
            "timestamp": datetime.now().isoformat(),
            "error": error_tb[:500],
        }
        with open(results_csv_path, "a", newline="") as _f:
            csv.DictWriter(_f, fieldnames=csv_fields).writerow(_csv_row)

        result_queue.put(("error", error_tb))


# ============================================================
# Process each case
# ============================================================
results_summary = []

for i, case_id in enumerate(CASES_TO_RUN, 1):
    print(f"{'='*80}")
    print(f"Processing Case {i}/{len(CASES_TO_RUN)}: {case_id}")
    print(f"{'='*80}")

    # Ensure case dir exists (for error files written by parent on timeout)
    case_results_dir = os.path.join(RESULTS_DIR, f"case_{case_id}")
    os.makedirs(case_results_dir, exist_ok=True)

    _ts = datetime.now().isoformat()
    _result_queue = multiprocessing.Queue()
    _proc = multiprocessing.Process(
        target=_af_case_worker,
        args=(
            case_id, RESULTS_DIR, RESULTS_CSV_PATH, _CSV_FIELDS,
            BENCHMARKS_DIR, JSON_FILE_PATH_MS, JSON_FILE_PATH_SS,
            LLM_ENGINE_NAME, PLANNER_GRANULARITY, EXECUTE_PIPELINE,
            VALIDATION, START_AGAIN_CLEAR_HISTORY, _TRANSCHEMA_ROOT,
            _result_queue,
        ),
        daemon=True,
    )
    _proc.start()
    _proc.join(timeout=_CASE_TIMEOUT)

    if _proc.is_alive():
        print(f"\n[TIMEOUT] Case {case_id} exceeded {_CASE_TIMEOUT}s — killing process")
        _proc.terminate()
        _proc.join()
        _csv_row = {
            "case_id": case_id,
            "status": "timeout",
            "is_correct": False,
            "score": None,
            "score_fd": None,
            "column_mapping_score": None,
            "average_similarity": None,
            "latency_seconds": _CASE_TIMEOUT,
            "cost": "N/A",
            "timestamp": _ts,
            "error": f"Timed out after {_CASE_TIMEOUT}s",
        }
        with open(RESULTS_CSV_PATH, "a", newline="") as _f:
            csv.DictWriter(_f, fieldnames=_CSV_FIELDS).writerow(_csv_row)
        results_summary.append({"case": case_id, "status": "timeout", "timestamp": _ts})
    elif not _result_queue.empty():
        _status, _payload = _result_queue.get()
        if _status == "ok":
            results_summary.append(_payload)
        else:
            results_summary.append({
                "case": case_id, "status": "error",
                "error": str(_payload)[:200], "timestamp": _ts,
            })
    else:
        print(f"\n✗ Case {case_id} exited without result")
        results_summary.append({
            "case": case_id, "status": "error",
            "error": "process exited without result", "timestamp": _ts,
        })

    print()

# ============================================================
# Summary
# ============================================================
num_correct  = sum(1 for r in results_summary if r.get("is_correct", False))
num_incorrect = sum(1 for r in results_summary if r["status"] == "incorrect")
num_error    = sum(1 for r in results_summary if r["status"] == "error")
num_timeout  = sum(1 for r in results_summary if r["status"] == "timeout")

print(f"{'='*80}")
print(f"SUMMARY")
print(f"{'='*80}")
print(f"  Total Cases: {len(CASES_TO_RUN)}")
print(f"  Correct:   {num_correct}")
print(f"  Incorrect: {num_incorrect}")
print(f"  Errors:    {num_error}")
print(f"  Timeouts:  {num_timeout}")
print(f"\nResults organized in: {RESULTS_DIR}/")

for result in results_summary:
    if result["status"] == "correct":
        icon = "✓"
        suffix = f" ({result.get('duration_seconds', 0):.2f}s)"
    elif result["status"] == "incorrect":
        icon = "✗"
        suffix = f" ({result.get('duration_seconds', 0):.2f}s)"
    elif result["status"] == "timeout":
        icon = "⏱"
        suffix = f" - timed out after {_CASE_TIMEOUT}s"
    else:
        icon = "!"
        suffix = f" - {result.get('error', 'Unknown error')}"
    print(f"  {icon} {result['case']}: {result['status'].upper()}{suffix}")

print(f"\nResults CSV: {RESULTS_CSV_PATH}")
print(f"\n{'='*80}")
print("Done!")
