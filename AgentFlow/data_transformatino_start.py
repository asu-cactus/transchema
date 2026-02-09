"""
Script to process selected data transformation cases and log results.
Comment out cases you don't want to run.
"""

import os
import json
from datetime import datetime

# Import the solver and logging setup
from agentflow.agentflow.solver import construct_solver, setup_logging

# ============================================================
# CASES TO RUN - Comment out the ones you don't want to run
# ============================================================
CASES_TO_RUN = [
    "4_31",
    # "4_35",
    # "4_74",
    # "4_79",
    # "4_97",
]
# ============================================================

# Configuration
CASES_DIR = "/home/local/ASUAD/jrtandel/transchema/AgentFlow/cases"
RESULTS_DIR = "/home/local/ASUAD/jrtandel/transchema/AgentFlow/results"
LLM_ENGINE_NAME = "gpt-4.1-mini"

# Start Again Tool behavior:
# True  = clear all prior actions from memory and start fresh
# False = keep prior actions but add a START_AGAIN marker (signal only)
START_AGAIN_CLEAR_HISTORY = False

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

print(f"Cases selected to run: {CASES_TO_RUN}\n")

# Process each case
results_summary = []

for i, case_file in enumerate(CASES_TO_RUN, 1):
    case_path = os.path.join(CASES_DIR, case_file)

    if not os.path.isfile(case_path):
        print(f"WARNING: Case file not found: {case_path}, skipping.\n")
        continue

    print(f"{'='*80}")
    print(f"Processing Case {i}/{len(CASES_TO_RUN)}: {case_file}")
    print(f"{'='*80}")

    # Create case-specific results directory for logs
    case_results_dir = os.path.join(RESULTS_DIR, f"case_{case_file}")
    case_logs_dir = os.path.join(case_results_dir, "logs")
    os.makedirs(case_logs_dir, exist_ok=True)

    try:
        # Setup logging for this specific case
        print(f"Setting up logging for case: {case_file}")
        logger, component_loggers = setup_logging(case_logs_dir)

        # Update the global loggers in the solver module
        import agentflow.agentflow.solver as solver_module

        solver_module.logger = logger
        solver_module.prompt_logger = component_loggers["prompts"]
        solver_module.tool_logger = component_loggers["tools"]
        solver_module.memory_logger = component_loggers["memory"]

        # Check for additional context (answer file)
        print(f"Checking for additional context for case: {case_file}")
        answer_path = os.path.join(CASES_DIR, f"{case_file}_answer")
        has_answer = os.path.isfile(answer_path) and os.path.getsize(answer_path) > 0
        if has_answer:
            print(f"Additional context found: {answer_path}")
        else:
            answer_path = None
            print(f"No additional context file for this case.")

        # Construct the solver for this case
        print(f"Initializing solver for case: {case_file}")
        solver = construct_solver(
            llm_engine_name=LLM_ENGINE_NAME,
            enabled_tools=[
                "Add_Operator_Tool",
                "Configure_Join_Operator_Tool",
                "Configure_Union_Operator_Tool",
                "Configure_GroupBy_Aggregate_Operator_Tool",
                "Code_Generator_Tool",
                # "Critique_Pipeline_Tool",
                # "Start_Again_Tool",
            ],
            tool_engine=[
                "Default",
                "Default",
                "Default",
                "Default",
                "Default",
                # "Default",
                # "Default",
            ],
            model_engine=["trainable", "trainable", "trainable", "trainable"],
            additional_context_file=answer_path,
            start_again_clear_history=START_AGAIN_CLEAR_HISTORY,
        )

        # Read the case query
        with open(case_path, "r") as f:
            query = f.read()

        print(f"Query loaded ({len(query)} characters)")
        print(f"Starting solver...")

        # Solve the case
        start_time = datetime.now()
        output = solver.solve(query)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✓ Case {case_file} completed in {duration:.2f} seconds")

        # Extract results
        direct_output = output.get("direct_output", "No output")

        # Save individual case result
        result_file = os.path.join(case_results_dir, f"{case_file}_result.txt")
        with open(result_file, "w") as f:
            f.write(f"Case: {case_file}\n")
            f.write(f"Timestamp: {start_time.isoformat()}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"LLM Engine: {LLM_ENGINE_NAME}\n")
            f.write(f"Logs Directory: {case_logs_dir}\n")
            f.write(f"\n{'='*80}\n")
            f.write(f"QUERY:\n")
            f.write(f"{'='*80}\n")
            f.write(query)
            f.write(f"\n\n{'='*80}\n")
            f.write(f"OUTPUT:\n")
            f.write(f"{'='*80}\n")
            f.write(str(direct_output))

        # Save full JSON output
        json_output_file = os.path.join(
            case_results_dir, f"{case_file}_full_output.json"
        )
        with open(json_output_file, "w") as f:
            json.dump(output, f, indent=2, default=str)

        print(f"✓ Result saved to: {result_file}")
        print(f"✓ Full output saved to: {json_output_file}")
        print(f"✓ Logs saved to: {case_logs_dir}/")

        # Add to summary
        results_summary.append(
            {
                "case": case_file,
                "status": "success",
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "result_file": result_file,
                "json_output_file": json_output_file,
                "logs_directory": case_logs_dir,
                "output_preview": (
                    str(direct_output)[:200] + "..."
                    if len(str(direct_output)) > 200
                    else str(direct_output)
                ),
            }
        )

    except Exception as e:
        import traceback

        error_traceback = traceback.format_exc()

        print(f"\n✗ Error processing case {case_file}: {str(e)}")

        # Save error log
        error_file = os.path.join(case_results_dir, f"{case_file}_error.txt")
        with open(error_file, "w") as f:
            f.write(f"Case: {case_file}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write(f"Traceback:\n{error_traceback}\n")

        results_summary.append(
            {
                "case": case_file,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "logs_directory": case_logs_dir,
            }
        )

    print(f"\n")

# Print summary
print(f"{'='*80}")
print(f"SUMMARY")
print(f"{'='*80}")
print(f"  Total Cases: {len(CASES_TO_RUN)}")
print(f"  Successful: {sum(1 for r in results_summary if r['status'] == 'success')}")
print(f"  Failed: {sum(1 for r in results_summary if r['status'] == 'error')}")
print(f"\nResults organized in: {RESULTS_DIR}/")

for result in results_summary:
    status_icon = "✓" if result["status"] == "success" else "✗"
    print(f"  {status_icon} {result['case']}: {result['status'].upper()}", end="")
    if result["status"] == "success":
        print(f" ({result['duration_seconds']:.2f}s)")
    else:
        print(f" - {result.get('error', 'Unknown error')}")

print(f"\n{'='*80}")
print("Done!")
