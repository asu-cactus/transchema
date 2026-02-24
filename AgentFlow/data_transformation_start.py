"""
Script to process data transformation cases and log results.
Cases are determined by (len_id, target_id) ranges using get_test_cases_ids.
Queries are generated dynamically via get_prompt(prompt_type="get_case_info").
"""

import os
import sys
import json
import traceback
from datetime import datetime

# Ensure the transchema root is on the path so shared utilities are importable.
_TRANSCHEMA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)

from agentflow.agentflow.solver import construct_solver, setup_logging
from test_scope import get_test_cases_ids
from util.utils import get_test_info
from auto_suggest_llm_util import get_prompt

# ============================================================
# CASE CONFIGURATION
# ============================================================
# Option A — Explicit list of target IDs (for case-based testing):
#   Set TARGET_IDS to a list, e.g. [4, 6, 48, 56]
#
# Option B — Range of target IDs (for mass testing):
#   Set TARGET_IDS to None and configure the range below.
#
LEN_ID = 4
TARGET_IDS = [
    # 16, 17, 18, 19, 
    # 20, 21, 22, 23, 24, 25,
    27, 28, 29,
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
]  # e.g. [4, 6, 48, 56] or None for range mode

# Range mode settings (only used when TARGET_IDS is None)
MAX_LEN_ID = 4
TARGET_ID_START = 1
TARGET_ID_END = 60
# ============================================================

# Paths
JSON_FILE_PATH_MS = os.path.join(_TRANSCHEMA_ROOT, "data", "chatgpt_github_ms.json")
JSON_FILE_PATH_SS = os.path.join(_TRANSCHEMA_ROOT, "data", "chatgpt_github_ss.json")
BENCHMARKS_DIR = os.path.join(
    _TRANSCHEMA_ROOT, "autopipeline-benchmarks", "github-pipelines"
)
RESULTS_DIR = os.path.join(
    _TRANSCHEMA_ROOT,
    "AgentFlow",
    "results_pipeline_execution_experiments_len_4_failed_cases",
)

# Model / solver configuration
LLM_ENGINE_NAME = "gpt-4.1-mini"

# Planner granularity:
#   "operator" = operator-level planning
#   "pipeline" = pipeline-level planning
PLANNER_GRANULARITY = "pipeline"

# Pipeline execution + scoring inside the agentic loop
EXECUTE_PIPELINE = False

# Start Again Tool behavior
START_AGAIN_CLEAR_HISTORY = False

# ============================================================
# Derive the list of cases
# ============================================================
if TARGET_IDS is not None:
    # Option A: explicit list
    CASES_TO_RUN = [f"{LEN_ID}_{tid}" for tid in TARGET_IDS]
else:
    # Option B: range via get_test_cases_ids
    task_list = get_test_cases_ids(
        JSON_FILE_PATH_MS, LEN_ID, MAX_LEN_ID, TARGET_ID_START, TARGET_ID_END
    )
    CASES_TO_RUN = sorted(set(t[6:] for t in task_list))

os.makedirs(RESULTS_DIR, exist_ok=True)

print(f"Cases selected to run: {CASES_TO_RUN}\n")

# ============================================================
# Process each case
# ============================================================
results_summary = []

for i, case_id in enumerate(CASES_TO_RUN, 1):
    print(f"{'='*80}")
    print(f"Processing Case {i}/{len(CASES_TO_RUN)}: {case_id}")
    print(f"{'='*80}")

    # Create case-specific results directory
    case_results_dir = os.path.join(RESULTS_DIR, f"case_{case_id}")
    case_logs_dir = os.path.join(case_results_dir, "logs")
    os.makedirs(case_logs_dir, exist_ok=True)

    try:
        # Setup logging
        logger, component_loggers = setup_logging(case_logs_dir)

        import agentflow.agentflow.solver as solver_module

        solver_module.logger = logger
        solver_module.prompt_logger = component_loggers["prompts"]
        solver_module.tool_logger = component_loggers["tools"]
        solver_module.memory_logger = component_loggers["memory"]

        # --- Select correct JSON based on file count (ms vs ss) ---
        path_to_files = os.path.join(BENCHMARKS_DIR, f"length{case_id}")
        file_count = sum(
            1
            for _, _, files in os.walk(path_to_files)
            for file in files
            if file.startswith("test")
        )
        if file_count > 1:
            json_file_path = JSON_FILE_PATH_MS
        else:
            json_file_path = JSON_FILE_PATH_SS

        # --- Build the query dynamically via get_prompt ---
        (
            target_data_name,
            target_data_schema,
            target_data_schema_with_types,
            _target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            _source_samples_list,
        ) = get_test_info(
            json_file_path,
            case_id,
            BENCHMARKS_DIR,
            anon_flag=0,
        )

        query = get_prompt(
            prompt_type="get_case_info",
            allowed_operation_list=[],
            operation_history=[],
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples="",  # will be filled by get_prompt
            file_count=file_count,
            directory=BENCHMARKS_DIR,
            len_idx_target_idx=case_id,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            target_data_schema_with_types=target_data_schema_with_types,
            target_length=3,
            source_length=3,
            model=LLM_ENGINE_NAME,
        )

        print(f"Query generated ({len(query)} characters)")

        # --- Select tools based on planner granularity ---
        if PLANNER_GRANULARITY == "pipeline":
            enabled_tools = [
                "Create_Pipeline_Tool",
                "Modify_Pipeline_Tool",
                "Code_Generator_Tool",
                "Finalize_Pipeline_Tool",
            ]
            tool_engine = ["Default"] * len(enabled_tools)
        else:
            enabled_tools = [
                "Add_Operator_Tool",
                "Configure_Join_Operator_Tool",
                "Configure_Union_Operator_Tool",
                "Configure_GroupBy_Aggregate_Operator_Tool",
                "Code_Generator_Tool",
            ]
            tool_engine = ["Default"] * len(enabled_tools)

        # Ground truth path (always provided for final scoring/verification)
        ground_truth_csv = os.path.join(
            BENCHMARKS_DIR, f"length{case_id}", "target.csv"
        )
        if not os.path.isfile(ground_truth_csv):
            print(f"WARNING: Ground truth not found at {ground_truth_csv}")
            ground_truth_csv = None

        # --- Construct and run solver ---
        solver = construct_solver(
            llm_engine_name=LLM_ENGINE_NAME,
            enabled_tools=enabled_tools,
            tool_engine=tool_engine,
            model_engine=["trainable", "trainable", "trainable", "trainable"],
            start_again_clear_history=START_AGAIN_CLEAR_HISTORY,
            planner_granularity=PLANNER_GRANULARITY,
            execute_pipeline=EXECUTE_PIPELINE,
            ground_truth_csv=ground_truth_csv,
        )

        print(f"Starting solver...")

        start_time = datetime.now()
        output = solver.solve(query)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Determine correctness from verification
        is_correct = output.get("is_correct", False)
        case_status = "correct" if is_correct else "incorrect"
        status_icon = "✓" if is_correct else "✗"

        print(
            f"\n{status_icon} Case {case_id} completed in {duration:.2f} seconds — {case_status.upper()}"
        )

        # Save results
        result_file = os.path.join(case_results_dir, f"{case_id}_result.txt")
        with open(result_file, "w") as f:
            f.write(f"Case: {case_id}\n")
            f.write(f"Status: {case_status.upper()}\n")
            f.write(f"Timestamp: {start_time.isoformat()}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"LLM Engine: {LLM_ENGINE_NAME}\n")
            f.write(f"Logs Directory: {case_logs_dir}\n")
            verification = output.get("verification_result", {})
            if verification:
                f.write(f"\nVerification:\n")
                f.write(f"  is_correct: {is_correct}\n")
                f.write(
                    f"  average_similarity: {verification.get('average_similarity', 'N/A')}\n"
                )
                f.write(
                    f"  matched_columns: {verification.get('all_matched_columns', [])}\n"
                )
                f.write(
                    f"  calculate_score: {verification.get('calculate_score', 'N/A')}\n"
                )
            f.write(f"\n{'='*80}\n")
            f.write(f"QUERY:\n")
            f.write(f"{'='*80}\n")
            f.write(query)
            f.write(f"\n\n{'='*80}\n")
            f.write(f"OUTPUT:\n")
            f.write(f"{'='*80}\n")
            f.write(
                str(
                    output.get("direct_output", output.get("final_output", "No output"))
                )
            )

        json_output_file = os.path.join(case_results_dir, f"{case_id}_full_output.json")
        with open(json_output_file, "w") as f:
            json.dump(output, f, indent=2, default=str)

        print(f"{status_icon} Result saved to: {result_file}")
        print(f"{status_icon} Full output saved to: {json_output_file}")
        print(f"{status_icon} Logs saved to: {case_logs_dir}/")

        results_summary.append(
            {
                "case": case_id,
                "status": case_status,
                "is_correct": is_correct,
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "result_file": result_file,
                "json_output_file": json_output_file,
                "logs_directory": case_logs_dir,
            }
        )

    except Exception as e:
        error_tb = traceback.format_exc()
        print(f"\n✗ Error processing case {case_id}: {e}")

        error_file = os.path.join(case_results_dir, f"{case_id}_error.txt")
        with open(error_file, "w") as f:
            f.write(f"Case: {case_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Error: {e}\n\nTraceback:\n{error_tb}\n")

        results_summary.append(
            {
                "case": case_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "logs_directory": case_logs_dir,
            }
        )

    print()

# ============================================================
# Summary
# ============================================================
num_correct = sum(1 for r in results_summary if r.get("is_correct", False))
num_incorrect = sum(1 for r in results_summary if r["status"] == "incorrect")
num_error = sum(1 for r in results_summary if r["status"] == "error")

print(f"{'='*80}")
print(f"SUMMARY")
print(f"{'='*80}")
print(f"  Total Cases: {len(CASES_TO_RUN)}")
print(f"  Correct:   {num_correct}")
print(f"  Incorrect: {num_incorrect}")
print(f"  Errors:    {num_error}")
print(f"\nResults organized in: {RESULTS_DIR}/")

for result in results_summary:
    if result["status"] == "correct":
        icon = "✓"
        suffix = f" ({result['duration_seconds']:.2f}s)"
    elif result["status"] == "incorrect":
        icon = "✗"
        suffix = f" ({result['duration_seconds']:.2f}s)"
    else:
        icon = "!"
        suffix = f" - {result.get('error', 'Unknown error')}"
    print(f"  {icon} {result['case']}: {result['status'].upper()}{suffix}")

print(f"\n{'='*80}")
print("Done!")
