"""
Script to process all data transformation cases and log results
"""
import os
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Import the solver and logging setup
from agentflow.agentflow.solver import construct_solver, setup_logging

# Configuration
CASES_DIR = "/home/local/ASUAD/jrtandel/transchema/AgentFlow/cases"
RESULTS_DIR = "/home/local/ASUAD/jrtandel/transchema/AgentFlow/results"
LLM_ENGINE_NAME = "gpt-4o"

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

# Get all case files
case_files = sorted([f for f in os.listdir(CASES_DIR) if os.path.isfile(os.path.join(CASES_DIR, f))])
print(f"Found {len(case_files)} cases to process: {case_files}\n")

# Process each case
results_summary = []

for i, case_file in enumerate(case_files, 1):
    case_path = os.path.join(CASES_DIR, case_file)

    print(f"{'='*80}")
    print(f"Processing Case {i}/{len(case_files)}: {case_file}")
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

        # Construct the solver for this case
        print(f"Initializing solver for case: {case_file}")
        solver = construct_solver(
            llm_engine_name=LLM_ENGINE_NAME,
            enabled_tools=[
                "Add_Operator_Tool",
                "Configure_Join_Operator_Tool",
                "Configure_Union_Operator_Tool",
                "Configure_GroupBy_Aggregate_Operator_Tool",
                "Critique_Pipeline_Tool",
                "Start_Again_Tool",
            ],
            tool_engine=["Default", "Default", "Default", "Default", "Default", "Default"],
        )

        # Read the case query
        with open(case_path, 'r') as f:
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
        with open(result_file, 'w') as f:
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
        json_output_file = os.path.join(case_results_dir, f"{case_file}_full_output.json")
        with open(json_output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"✓ Result saved to: {result_file}")
        print(f"✓ Full output saved to: {json_output_file}")
        print(f"✓ Logs saved to: {case_logs_dir}/")

        # Add to summary
        results_summary.append({
            "case": case_file,
            "status": "success",
            "duration_seconds": duration,
            "timestamp": start_time.isoformat(),
            "result_file": result_file,
            "json_output_file": json_output_file,
            "logs_directory": case_logs_dir,
            "output_preview": str(direct_output)[:200] + "..." if len(str(direct_output)) > 200 else str(direct_output)
        })

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()

        print(f"\n✗ Error processing case {case_file}: {str(e)}")

        # Save error log
        error_file = os.path.join(case_results_dir, f"{case_file}_error.txt")
        with open(error_file, 'w') as f:
            f.write(f"Case: {case_file}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write(f"Traceback:\n{error_traceback}\n")

        results_summary.append({
            "case": case_file,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "logs_directory": case_logs_dir,
        })

    print(f"\n")

# Save summary report
print(f"{'='*80}")
print(f"ALL CASES PROCESSED - GENERATING SUMMARY")
print(f"{'='*80}\n")

summary_file = os.path.join(RESULTS_DIR, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(summary_file, 'w') as f:
    json.dump({
        "total_cases": len(case_files),
        "successful": sum(1 for r in results_summary if r["status"] == "success"),
        "failed": sum(1 for r in results_summary if r["status"] == "error"),
        "llm_engine": LLM_ENGINE_NAME,
        "results": results_summary
    }, f, indent=2)

# Create a text summary as well
summary_text_file = os.path.join(RESULTS_DIR, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
with open(summary_text_file, 'w') as f:
    f.write(f"{'='*80}\n")
    f.write(f"AGENTFLOW DATA TRANSFORMATION - BATCH PROCESSING SUMMARY\n")
    f.write(f"{'='*80}\n\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write(f"LLM Engine: {LLM_ENGINE_NAME}\n\n")
    f.write(f"Total Cases: {len(case_files)}\n")
    f.write(f"Successful: {sum(1 for r in results_summary if r['status'] == 'success')}\n")
    f.write(f"Failed: {sum(1 for r in results_summary if r['status'] == 'error')}\n\n")
    f.write(f"{'='*80}\n")
    f.write(f"DETAILED RESULTS\n")
    f.write(f"{'='*80}\n\n")

    for result in results_summary:
        status_icon = "✓" if result["status"] == "success" else "✗"
        f.write(f"{status_icon} Case: {result['case']}\n")
        f.write(f"  Status: {result['status'].upper()}\n")
        if result["status"] == "success":
            f.write(f"  Duration: {result['duration_seconds']:.2f} seconds\n")
            f.write(f"  Result File: {result['result_file']}\n")
            f.write(f"  JSON Output: {result['json_output_file']}\n")
            f.write(f"  Logs Directory: {result['logs_directory']}\n")
        else:
            f.write(f"  Error: {result.get('error', 'Unknown error')}\n")
            f.write(f"  Logs Directory: {result['logs_directory']}\n")
        f.write(f"\n")

    f.write(f"{'='*80}\n")
    f.write(f"RESULTS DIRECTORY STRUCTURE\n")
    f.write(f"{'='*80}\n\n")
    f.write(f"{RESULTS_DIR}/\n")
    for case_file in case_files:
        f.write(f"├── case_{case_file}/\n")
        f.write(f"│   ├── {case_file}_result.txt\n")
        f.write(f"│   ├── {case_file}_full_output.json\n")
        f.write(f"│   └── logs/\n")
        f.write(f"│       ├── agentflow_all_*.log\n")
        f.write(f"│       ├── agentflow_prompts_*.log\n")
        f.write(f"│       ├── agentflow_tools_*.log\n")
        f.write(f"│       └── agentflow_memory_*.log\n")
    f.write(f"└── summary_*.json/txt\n")

# Print summary
print(f"Summary Report:")
print(f"  Total Cases: {len(case_files)}")
print(f"  Successful: {sum(1 for r in results_summary if r['status'] == 'success')}")
print(f"  Failed: {sum(1 for r in results_summary if r['status'] == 'error')}")
print(f"\nSummaries saved to:")
print(f"  - {summary_file}")
print(f"  - {summary_text_file}")
print(f"\nResults organized in: {RESULTS_DIR}/")
print(f"\n{'='*80}")

# Print individual case results
print("\nDetailed Results:")
for result in results_summary:
    status_icon = "✓" if result["status"] == "success" else "✗"
    print(f"  {status_icon} {result['case']}: {result['status'].upper()}", end="")
    if result["status"] == "success":
        print(f" ({result['duration_seconds']:.2f}s)")
        print(f"      Logs: {result['logs_directory']}")
    else:
        print(f" - {result.get('error', 'Unknown error')}")
        print(f"      Logs: {result['logs_directory']}")

print(f"\n{'='*80}")
print("Done!")
