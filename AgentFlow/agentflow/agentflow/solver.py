import argparse
import os
import re
import subprocess
import sys
import time
import json
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

import pandas as pd

from agentflow.models.initializer import Initializer
from agentflow.models.planner import Planner
from agentflow.models.verifier import Verifier
from agentflow.models.memory import Memory
from agentflow.models.executor import Executor
from agentflow.models.utils import make_json_serializable_truncated

# Add transchema root to path for importing calculate_score
_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[3])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)


# Configure logging
def setup_logging(log_dir: str = "logs"):
    """Setup logging configuration with separate files for different log types"""
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Main logger
    logger = logging.getLogger("agentflow")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Clear any existing handlers

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)

    # File handler - all logs
    all_logs_handler = logging.FileHandler(f"{log_dir}/agentflow_all_{timestamp}.log")
    all_logs_handler.setLevel(logging.DEBUG)
    all_logs_handler.setFormatter(detailed_formatter)
    logger.addHandler(all_logs_handler)

    # Separate loggers for different components
    loggers = {
        "prompts": logging.getLogger("agentflow.prompts"),
        "tools": logging.getLogger("agentflow.tools"),
        "memory": logging.getLogger("agentflow.memory"),
    }

    for name, component_logger in loggers.items():
        component_logger.setLevel(logging.DEBUG)
        component_logger.handlers.clear()

        # File handler for each component
        file_handler = logging.FileHandler(
            f"{log_dir}/agentflow_{name}_{timestamp}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        component_logger.addHandler(file_handler)

    return logger, loggers


# Initialize loggers
logger, component_loggers = setup_logging()
prompt_logger = component_loggers["prompts"]
tool_logger = component_loggers["tools"]
memory_logger = component_loggers["memory"]


class Solver:
    def __init__(
        self,
        planner,
        verifier,
        memory,
        executor,
        output_types: str = "base,final,direct",
        max_steps: int = 10,
        max_time: int = 300,
        max_tokens: int = 4000,
        root_cache_dir: str = "cache",
        verbose: bool = True,
        temperature: float = 0.0,
        additional_context: str = None,
        start_again_clear_history: bool = False,
        execute_pipeline: bool = False,
        ground_truth_csv: str = None,
    ):
        self.planner = planner
        self.verifier = verifier
        self.memory = memory
        self.executor = executor
        self.max_steps = max_steps
        self.max_time = max_time
        self.max_tokens = max_tokens
        self.root_cache_dir = root_cache_dir
        self.additional_context = additional_context
        self.start_again_clear_history = start_again_clear_history
        self.execute_pipeline = execute_pipeline
        self.ground_truth_csv = ground_truth_csv

        self.output_types = output_types.lower().split(",")
        self.temperature = temperature
        assert all(
            output_type in ["base", "final", "direct"]
            for output_type in self.output_types
        ), "Invalid output type. Supported types are 'base', 'final', 'direct'."
        self.verbose = verbose

        if self.ground_truth_csv and not os.path.isfile(self.ground_truth_csv):
            raise ValueError(
                f"ground_truth_csv path does not exist: {self.ground_truth_csv}"
            )

        logger.info(
            f"Solver initialized with max_steps={max_steps}, max_time={max_time}, temperature={temperature}"
        )
        if additional_context:
            logger.info(
                f"Solver initialized with additional context ({len(additional_context)} characters)"
            )

    def _log_llm_call(self, operation: str, inputs: dict, step: Optional[int] = None):
        """Log LLM call details"""
        step_info = f"[Step {step}] " if step is not None else ""
        prompt_logger.info(f"{step_info}LLM Call - Operation: {operation}")
        prompt_logger.debug(
            f"{step_info}LLM Call Inputs: {json.dumps(inputs, indent=2, default=str)}"
        )
        logger.info(f"{step_info}🤖 LLM Call: {operation}")

    def _log_llm_response(
        self, operation: str, response: str, step: Optional[int] = None
    ):
        """Log LLM response"""
        step_info = f"[Step {step}] " if step is not None else ""
        prompt_logger.info(f"{step_info}LLM Response - Operation: {operation}")
        prompt_logger.debug(f"{step_info}LLM Response: {response}")

    def _log_tool_execution(self, tool_name: str, command: str, step: int):
        """Log tool execution details"""
        tool_logger.info(f"[Step {step}] Tool Execution - Tool: {tool_name}")
        tool_logger.debug(f"[Step {step}] Command: {command}")
        logger.info(f"🔧 [Step {step}] Executing tool: {tool_name}")

    def _log_tool_result(self, tool_name: str, result: any, step: int):
        """Log tool execution result"""
        result_str = json.dumps(result, indent=2, default=str) if result else "None"
        tool_logger.info(f"[Step {step}] Tool Result - Tool: {tool_name}")
        tool_logger.debug(f"[Step {step}] Result: {result_str}")
        logger.info(f"✅ [Step {step}] Tool {tool_name} completed")

    def _log_memory_update(
        self, step: int, tool_name: str, sub_goal: str, command: str, result: any
    ):
        """Log memory update"""
        memory_logger.info(f"[Step {step}] Memory Update")
        memory_logger.debug(
            f"[Step {step}] Added to memory: tool={tool_name}, sub_goal={sub_goal}"
        )
        memory_logger.debug(f"[Step {step}] Command: {command}")
        memory_logger.debug(
            f"[Step {step}] Result: {json.dumps(result, indent=2, default=str)}"
        )

        # Log current memory state
        memory_state = self.memory.get_actions()
        memory_logger.debug(
            f"[Step {step}] Current Memory State: {len(memory_state)} actions"
        )
        for step_name, action in memory_state.items():
            memory_logger.debug(
                f"  - {step_name}: {action.get('tool_name', 'N/A')} - {action.get('sub_goal', 'N/A')}"
            )

        logger.info(
            f"💾 [Step {step}] Memory updated - Total actions: {len(memory_state)}"
        )

    # ---- Pipeline execution + scoring helpers ----

    def _extract_generated_code(self, code_gen_result) -> Optional[str]:
        """Extract generated code string from Code_Generator_Tool's result."""
        if isinstance(code_gen_result, list):
            for item in code_gen_result:
                if isinstance(item, dict) and item.get("generated_code"):
                    return item["generated_code"]
        elif isinstance(code_gen_result, dict) and code_gen_result.get(
            "generated_code"
        ):
            return code_gen_result["generated_code"]
        return None

    def _extract_output_csv_path(self, generated_code: str) -> Optional[str]:
        """Extract the output CSV path from generated Python code."""
        # Match .to_csv('path') or .to_csv("path")
        literal_matches = re.findall(
            r"\.to_csv\s*\(\s*['\"]([^'\"]+\.csv)['\"]", generated_code
        )
        if literal_matches:
            return literal_matches[-1]

        # Match variable assignments like OUTPUT_CSV_PATH = "x.csv"
        var_assignments = dict(
            re.findall(
                r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*['\"]([^'\"]+\.csv)['\"]",
                generated_code,
            )
        )

        # Match .to_csv(VAR_NAME, ...) and resolve against known assignments
        var_calls = re.findall(
            r"\.to_csv\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:,|\))",
            generated_code,
        )
        for var_name in reversed(var_calls):
            if var_name in var_assignments:
                return var_assignments[var_name]

        if "OUTPUT_CSV_PATH" in var_assignments:
            return var_assignments["OUTPUT_CSV_PATH"]

        return None

    def _extract_code_from_output(self, llm_output: str) -> Optional[str]:
        """Extract Python code block from LLM output (```Python ... ```)."""
        if not llm_output:
            return None
        match = re.search(r"```[Pp]ython\s*(.*?)\s*```", llm_output, re.DOTALL)
        return match.group(1).strip() if match else None

    def _execute_and_score_pipeline(
        self, code_gen_result, step_count: int
    ) -> Optional[dict]:
        """
        Execute generated Python code and calculate score against ground truth.

        Args:
            code_gen_result: Result from Code_Generator_Tool (list of dicts)
            step_count: Current step number

        Returns:
            dict with execution_success, output_csv_path, score, score_details, execution_error
        """
        generated_code = self._extract_generated_code(code_gen_result)
        if not generated_code:
            return {
                "execution_success": False,
                "execution_error": "No generated code found in Code_Generator_Tool result",
                "score": None,
            }

        # Determine the output CSV path from the generated code
        output_csv_path = self._extract_output_csv_path(generated_code)

        # Prefer case-local script archive under the benchmark case directory
        case_dir = (
            os.path.dirname(self.ground_truth_csv)
            if self.ground_truth_csv
            else self.root_cache_dir
        )
        if not os.path.isabs(case_dir):
            case_dir = os.path.join(_TRANSCHEMA_ROOT, case_dir)
        script_archive_dir = os.path.join(case_dir, "script_archive")
        os.makedirs(script_archive_dir, exist_ok=True)

        # If no output path found, inject a default one
        if not output_csv_path:
            output_csv_path = os.path.join(
                script_archive_dir, f"pipeline_output_step{step_count}.csv"
            )
            generated_code += (
                f"\n\n# Auto-injected output save\n"
                f"try:\n"
                f"    execution.to_csv('{output_csv_path}', index=False)\n"
                f"except NameError:\n"
                f"    try:\n"
                f"        result.to_csv('{output_csv_path}', index=False)\n"
                f"    except NameError:\n"
                f"        pass\n"
            )

        # Resolve relative output paths against repository root
        resolved_output_csv_path = (
            output_csv_path
            if os.path.isabs(output_csv_path)
            else os.path.join(_TRANSCHEMA_ROOT, output_csv_path)
        )

        # Write code to a case-local script archive file
        script_path = os.path.join(script_archive_dir, "agent_run.py")
        with open(script_path, "w") as f:
            f.write(generated_code)

        logger.info(f"[Step {step_count}] Executing pipeline code: {script_path}")
        if self.verbose:
            print(f"\n==> ⚙️ Step {step_count}: Executing generated pipeline code...")

        # Execute in subprocess with timeout
        try:
            proc = subprocess.run(
                [sys.executable, os.path.abspath(script_path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=_TRANSCHEMA_ROOT,
            )

            if proc.returncode != 0:
                error_msg = proc.stderr[-2000:] if proc.stderr else "Unknown error"
                logger.error(
                    f"[Step {step_count}] Pipeline code execution failed: {error_msg}"
                )
                if self.verbose:
                    print(f"\n==> ❌ Code execution failed:\n{error_msg[:500]}")
                return {
                    "execution_success": False,
                    "execution_error": error_msg,
                    "execution_stdout": proc.stdout[-1000:] if proc.stdout else "",
                    "score": None,
                }

            # Execution succeeded - now score
            if os.path.isfile(resolved_output_csv_path):
                score_result = self._calculate_pipeline_score(resolved_output_csv_path)
                logger.info(
                    f"[Step {step_count}] Pipeline score: {score_result.get('score')}"
                )
                if self.verbose:
                    print(f"\n==> 📊 Pipeline Score: {score_result.get('score')}")
                    print(f"    FD Score: {score_result.get('score_fd')}")
                    print(f"    Key Score: {score_result.get('score_key')}")
                    print(
                        f"    Column Mapping Score: {score_result.get('column_mapping_score')}"
                    )
                return {
                    "execution_success": True,
                    "output_csv_path": resolved_output_csv_path,
                    "execution_stdout": proc.stdout[-1000:] if proc.stdout else "",
                    **score_result,
                }
            else:
                msg = (
                    f"Code ran but output CSV not found at: {resolved_output_csv_path}"
                )
                logger.warning(f"[Step {step_count}] {msg}")
                if self.verbose:
                    print(f"\n==> ⚠️ {msg}")
                return {
                    "execution_success": True,
                    "execution_error": msg,
                    "execution_stdout": proc.stdout[-1000:] if proc.stdout else "",
                    "score": None,
                }

        except subprocess.TimeoutExpired:
            logger.error(
                f"[Step {step_count}] Pipeline code execution timed out (120s)"
            )
            if self.verbose:
                print(f"\n==> ⏰ Code execution timed out (120s)")
            return {
                "execution_success": False,
                "execution_error": "Code execution timed out after 120 seconds",
                "score": None,
            }
        except Exception as e:
            logger.error(f"[Step {step_count}] Pipeline execution error: {e}")
            return {
                "execution_success": False,
                "execution_error": str(e),
                "score": None,
            }

    def _calculate_pipeline_score(self, output_csv_path: str) -> dict:
        """Calculate score comparing ground truth to pipeline output."""
        try:
            from auto_suggest_llm_util import (
                calculate_score,
                get_filtered_functional_dependency,
                extract_dependencies,
            )
            from valentine import valentine_match, algorithms
        except ImportError as e:
            logger.warning(f"Could not import scoring functions: {e}")
            return {
                "score": None,
                "score_fd": None,
                "score_key": None,
                "column_mapping_score": None,
                "score_error": f"Import error: {e}",
            }

        try:
            gt_df = pd.read_csv(self.ground_truth_csv, index_col=0, low_memory=False)
            tgt_df = pd.read_csv(output_csv_path, low_memory=False)

            # Drop unnamed index columns if present in output
            unnamed_cols = [c for c in tgt_df.columns if c.startswith("Unnamed")]
            if unnamed_cols:
                tgt_df.drop(columns=unnamed_cols, inplace=True)

            # Calculate individual score components for detailed feedback
            key_gt, fd_gt = get_filtered_functional_dependency(gt_df)
            key_tgt, fd_tgt = get_filtered_functional_dependency(tgt_df)

            dependencies_gt = extract_dependencies(fd_gt)
            dependencies_tgt = extract_dependencies(fd_tgt)

            overlapping_dependencies = dependencies_gt.intersection(dependencies_tgt)
            overlapping_keys = set(key_gt).intersection(key_tgt)

            score_fd = (
                len(overlapping_dependencies) / len(dependencies_gt)
                if len(dependencies_gt) > 0
                else 1
            )
            score_key = len(overlapping_keys) / len(key_gt) if len(key_gt) > 0 else 1

            matcher = algorithms.Cupid()
            matches = valentine_match(gt_df, tgt_df, matcher)
            gt_df_columns = set(gt_df.columns)
            matched_columns = set(match[0] for match in matches)
            column_mapping_score = (
                len(matched_columns) / len(gt_df_columns)
                if len(gt_df_columns) > 0
                else 0
            )

            # Combined score (same formula as calculate_score)
            w1, w2, w3, p = 1, 1, 1, 1
            combined_score = pow(
                w1 * (score_fd**p)
                + w2 * (score_key**p)
                + w3 * (column_mapping_score**p),
                1 / p,
            )

            return {
                "score": float(combined_score),
                "score_fd": float(score_fd),
                "score_key": float(score_key),
                "column_mapping_score": float(column_mapping_score),
                "score_details": {
                    "gt_shape": list(gt_df.shape),
                    "output_shape": list(tgt_df.shape),
                    "gt_columns": list(gt_df.columns),
                    "output_columns": list(tgt_df.columns),
                },
                "score_error": None,
            }
        except Exception as e:
            logger.error(f"Error calculating pipeline score: {e}")
            return {
                "score": None,
                "score_fd": None,
                "score_key": None,
                "column_mapping_score": None,
                "score_error": str(e),
            }

    def _merge_code_result_with_score(self, original_result, code_exec_result: dict):
        """Merge code execution + score results into the tool result for memory."""
        augmented = (
            list(original_result)
            if isinstance(original_result, list)
            else [original_result]
        )
        augmented.append(
            {
                "pipeline_execution": {
                    "execution_success": code_exec_result.get(
                        "execution_success", False
                    ),
                    "output_csv_path": code_exec_result.get("output_csv_path"),
                    "score": code_exec_result.get("score"),
                    "score_fd": code_exec_result.get("score_fd"),
                    "score_key": code_exec_result.get("score_key"),
                    "column_mapping_score": code_exec_result.get(
                        "column_mapping_score"
                    ),
                    "score_details": code_exec_result.get("score_details"),
                    "execution_error": code_exec_result.get("execution_error"),
                }
            }
        )
        return augmented

    def _get_finalized_pipeline_code(
        self, finalized_pipeline_id: Optional[str] = None
    ) -> Optional[str]:
        """Extract generated code from memory for the finalized (or latest) pipeline.

        When *finalized_pipeline_id* is provided, only code belonging to that
        pipeline is returned.  Otherwise the most recent generated_code from
        any pipeline result in memory is returned as a fallback.
        """
        for action in reversed(list(self.memory.get_actions().values())):
            result = action.get("result", {})
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and item.get("generated_code"):
                        if (
                            not finalized_pipeline_id
                            or item.get("pipeline_id") == finalized_pipeline_id
                        ):
                            return item["generated_code"]
            elif isinstance(result, dict) and result.get("generated_code"):
                if (
                    not finalized_pipeline_id
                    or result.get("pipeline_id") == finalized_pipeline_id
                ):
                    return result["generated_code"]
        return None

    def _verify_results(self, output_csv_path: str) -> Optional[dict]:
        """
        Verify pipeline output against ground truth using compare_lists_matching.

        Imitates the validation logic from methods/multi_step.py:
        1. Run compare_lists_matching
        2. If not correct but shared_columns exist and lengths match,
           retry with column header renaming (value-based headers)
        3. Compute calculate_score as a fallback metric
        4. Always return is_correct
        """
        from auto_suggest_llm_util import calculate_score

        is_correct = False
        case_accuracy = 0
        score = 0
        similarity_scores = []
        shared_columns = []

        try:
            from validation.hard_match import compare_lists_matching

            gt_df = pd.read_csv(self.ground_truth_csv, low_memory=False)
            output_df = pd.read_csv(output_csv_path, low_memory=False)

            # Drop first unnamed index column from ground truth (same as multi_step.py)
            if gt_df.columns[0].startswith("Unnamed"):
                gt_df.drop(columns=gt_df.columns[0], axis=1, inplace=True)

            # Clean up unnamed columns from output
            unnamed_cols = [c for c in output_df.columns if c.startswith("Unnamed")]
            if unnamed_cols:
                output_df.drop(columns=unnamed_cols, inplace=True)

            try:
                (
                    case_accuracy,
                    is_correct,
                    similarity_scores,
                    shared_columns,
                ) = compare_lists_matching(output_df, gt_df)

                if (
                    is_correct is False
                    and len(shared_columns) > 0
                    and len(output_df) == len(gt_df)
                ):
                    # Retry: ignore column headers, sort and rename by first 3 values
                    logger.info(
                        "Retrying with value-based column headers for better comparison"
                    )
                    sorted_output = output_df.sort_values(by=shared_columns)
                    sorted_gt = gt_df.sort_values(by=shared_columns)

                    def _rename_columns_by_values(df):
                        new_headers = []
                        for col in df.columns:
                            if "float" in str(df[col].dtype):
                                first_three = df[col].head(3).astype(int)
                            else:
                                first_three = df[col].head(3)
                            header = (
                                str(first_three.iloc[0])
                                + "-"
                                + str(first_three.iloc[1])
                                + "-"
                                + str(first_three.iloc[2])
                            )
                            new_headers.append(header)
                        df.columns = new_headers
                        return df

                    sorted_output = _rename_columns_by_values(sorted_output)
                    sorted_gt = _rename_columns_by_values(sorted_gt)

                    (
                        case_accuracy,
                        is_correct,
                        similarity_scores,
                        shared_columns,
                    ) = compare_lists_matching(sorted_output, sorted_gt)
                else:
                    # Calculate score as fallback metric
                    try:
                        score = calculate_score(gt_df, output_df)
                    except Exception:
                        score = 0
            except Exception as e:
                logger.error(f"Error in compare_lists_matching: {e}")
                is_correct = False

        except Exception as e:
            logger.error(f"Error during result verification: {e}")
            is_correct = False
            case_accuracy = 0

        # Build safe similarity list (handle error strings from compare_lists_matching)
        safe_similarities = []
        for s in similarity_scores:
            try:
                safe_similarities.append(float(s))
            except (ValueError, TypeError):
                safe_similarities.append(0.0)

        return {
            "is_correct": bool(is_correct),
            "average_similarity": float(case_accuracy) if case_accuracy else 0.0,
            "column_similarities": safe_similarities,
            "all_matched_columns": list(shared_columns) if shared_columns else [],
            "calculate_score": float(score) if score else 0.0,
        }

    # ---- End pipeline execution helpers ----

    def solve(self, question: str, image_path: Optional[str] = None):
        """
        Solve a single problem from the benchmark dataset.

        Args:
            question (str): The question to solve
            image_path (Optional[str]): Path to image if applicable
        """
        logger.info("=" * 80)
        logger.info(f"Starting new query: {question}")
        if image_path:
            logger.info(f"Image path: {image_path}")
        logger.info("=" * 80)

        # Update cache directory for the executor
        self.executor.set_query_cache_dir(self.root_cache_dir)

        # Initialize json_data with basic problem information
        json_data = {"query": question, "image": image_path}
        if self.verbose:
            print(f"\n==> 🔍 Received Query: {question}")
            if image_path:
                print(f"\n==> 🖼️ Received Image: {image_path}")

        # Generate base response if requested
        if "base" in self.output_types:
            self._log_llm_call(
                "generate_base_response",
                {
                    "question": question,
                    "image_path": image_path,
                    "max_tokens": self.max_tokens,
                },
            )

            base_response = self.planner.generate_base_response(
                question, image_path, self.max_tokens
            )

            self._log_llm_response("generate_base_response", base_response)
            json_data["base_response"] = base_response

            if self.verbose:
                print(f"\n==> 📝 Base Response from LLM:\n\n{base_response}")

        # If only base response is needed, save and return
        if set(self.output_types) == {"base"}:
            logger.info("Only base response requested - returning")
            return json_data

        # Continue with query analysis and tool execution if final or direct responses are needed
        if {"final", "direct"} & set(self.output_types):
            if self.verbose:
                print(f"\n==> 🐙 Reasoning Steps from AgentFlow (Deep Thinking...)")

            # [1] Analyze query
            query_start_time = time.time()

            self._log_llm_call(
                "analyze_query", {"question": question, "image_path": image_path}
            )

            query_analysis = self.planner.analyze_query(question, image_path)

            self._log_llm_response("analyze_query", query_analysis)
            json_data["query_analysis"] = query_analysis

            if self.verbose:
                print(f"\n==> 🔍 Step 0: Query Analysis\n")
                print(f"{query_analysis}")
                print(f"[Time]: {round(time.time() - query_start_time, 2)}s")

            # Main execution loop
            step_count = 0
            action_times = []
            is_pipeline_mode = self.planner.granularity == "pipeline"
            finalized_pipeline_id = None

            logger.info(
                f"Starting main execution loop (max_steps={self.max_steps}, max_time={self.max_time})"
            )

            while (
                step_count < self.max_steps
                and (time.time() - query_start_time) < self.max_time
            ):
                step_count += 1
                step_start_time = time.time()

                logger.info(f"{'='*60}")
                logger.info(f"Starting Step {step_count}/{self.max_steps}")
                logger.info(f"{'='*60}")

                # [2] Generate next step
                local_start_time = time.time()

                self._log_llm_call(
                    "generate_next_step",
                    {
                        "question": question,
                        "image_path": image_path,
                        "query_analysis": query_analysis[:200] + "...",
                        "step_count": step_count,
                        "max_steps": self.max_steps,
                    },
                    step=step_count,
                )

                next_step = self.planner.generate_next_step(
                    question,
                    image_path,
                    query_analysis,
                    self.memory,
                    step_count,
                    self.max_steps,
                    json_data,
                )

                self._log_llm_response("generate_next_step", next_step, step=step_count)

                context, sub_goal, tool_name = (
                    self.planner.extract_context_subgoal_and_tool(next_step)
                )

                logger.info(
                    f"[Step {step_count}] Predicted action - Tool: {tool_name}, Sub-goal: {sub_goal[:100]}"
                )

                if self.verbose:
                    print(
                        f"\n==> 🎯 Step {step_count}: Action Prediction ({tool_name})\n"
                    )
                    print(
                        f"[Context]: {context}\n[Sub Goal]: {sub_goal}\n[Tool]: {tool_name}"
                    )
                    print(f"[Time]: {round(time.time() - local_start_time, 2)}s")

                if tool_name is None or tool_name not in self.planner.available_tools:
                    error_msg = f"Tool '{tool_name}' is not available or not found."
                    logger.error(f"[Step {step_count}] {error_msg}")
                    print(f"\n==> 🚫 Error: {error_msg}")
                    command = "No command was generated because the tool was not found."
                    result = "No result was generated because the tool was not found."

                else:
                    # [3] Generate the tool command
                    local_start_time = time.time()

                    self._log_llm_call(
                        "generate_tool_command",
                        {
                            "question": question,
                            "tool_name": tool_name,
                            "sub_goal": sub_goal[:200] + "...",
                            "step_count": step_count,
                        },
                        step=step_count,
                    )

                    tool_command = self.executor.generate_tool_command(
                        question,
                        image_path,
                        context,
                        sub_goal,
                        tool_name,
                        self.planner.toolbox_metadata[tool_name],
                        step_count,
                        json_data,
                        self.memory,
                    )

                    self._log_llm_response(
                        "generate_tool_command", tool_command, step=step_count
                    )

                    analysis, explanation, command = (
                        self.executor.extract_explanation_and_command(tool_command)
                    )

                    if self.verbose:
                        print(
                            f"\n==> 📝 Step {step_count}: Command Generation ({tool_name})\n"
                        )
                        print(
                            f"[Analysis]: {analysis}\n[Explanation]: {explanation}\n[Command]: {command}"
                        )
                        print(f"[Time]: {round(time.time() - local_start_time, 2)}s")

                    # [4] Execute the tool command
                    local_start_time = time.time()

                    self._log_tool_execution(tool_name, command, step_count)

                    result = self.executor.execute_tool_command(tool_name, command)
                    result = make_json_serializable_truncated(
                        result
                    )  # Convert to JSON serializable format

                    self._log_tool_result(tool_name, result, step_count)

                    # [4b] Execute generated code and calculate score (when enabled)
                    # if (
                    #     self.execute_pipeline
                    #     and isinstance(result, list)
                    #     and len(result) > 0
                    # ):
                    #     code_exec_result = self._execute_and_score_pipeline(
                    #         result, step_count
                    #     )
                    #     if code_exec_result:
                    #         result = self._merge_code_result_with_score(
                    #             result, code_exec_result
                    #         )
                    #         result = make_json_serializable_truncated(result)

                    json_data[f"tool_result_{step_count}"] = result

                    if self.verbose:
                        print(
                            f"\n==> 🛠️ Step {step_count}: Command Execution ({tool_name})\n"
                        )
                        print(f"[Result]:\n{json.dumps(result, indent=4)}")
                        print(f"[Time]: {round(time.time() - local_start_time, 2)}s")

                # Track execution time for the current step
                execution_time_step = round(time.time() - step_start_time, 2)
                action_times.append(execution_time_step)
                logger.info(
                    f"[Step {step_count}] Execution time: {execution_time_step}s"
                )

                # Update memory - handle Start_Again_Tool specially
                if (
                    tool_name == "Start_Again_Tool"
                    and isinstance(result, dict)
                    and result.get("signal") == "START_AGAIN"
                ):
                    reason = result.get("reason", "Pipeline restart requested.")
                    logger.info(
                        f"[Step {step_count}] START_AGAIN signal received: {reason}"
                    )
                    self.memory.mark_start_again(
                        step_count, reason, clear_history=self.start_again_clear_history
                    )
                else:
                    self.memory.add_action(
                        step_count, tool_name, sub_goal, command, result
                    )
                self._log_memory_update(
                    step_count, tool_name, sub_goal, command, result
                )

                memory_actions = self.memory.get_actions()

                # [5] Verify memory (context verification)
                local_start_time = time.time()
                is_pipeline_mode = self.planner.granularity == "pipeline"

                if is_pipeline_mode:
                    # Pipeline-level verification
                    if self.additional_context:
                        self._log_llm_call(
                            "verificate_context_pipeline_with_additional_info",
                            {
                                "question": question,
                                "query_analysis": query_analysis[:200] + "...",
                                "additional_context": self.additional_context[:200]
                                + "...",
                                "step_count": step_count,
                            },
                            step=step_count,
                        )

                        stop_verification = self.verifier.verificate_context_pipeline_with_additional_info(
                            question,
                            query_analysis,
                            self.memory,
                            self.additional_context,
                            step_count,
                            json_data,
                        )

                        self._log_llm_response(
                            "verificate_context_pipeline_with_additional_info",
                            stop_verification,
                            step=step_count,
                        )
                    else:
                        self._log_llm_call(
                            "verificate_context_pipeline",
                            {
                                "question": question,
                                "query_analysis": query_analysis[:200] + "...",
                                "step_count": step_count,
                            },
                            step=step_count,
                        )

                        stop_verification = self.verifier.verificate_context_pipeline(
                            question,
                            image_path,
                            query_analysis,
                            self.memory,
                            step_count,
                            json_data,
                        )

                        self._log_llm_response(
                            "verificate_context_pipeline",
                            stop_verification,
                            step=step_count,
                        )
                else:
                    # Operator-level verification (original behavior)
                    if self.additional_context:
                        self._log_llm_call(
                            "verificate_context_with_additional_info",
                            {
                                "question": question,
                                "query_analysis": query_analysis[:200] + "...",
                                "additional_context": self.additional_context[:200]
                                + "...",
                                "step_count": step_count,
                            },
                            step=step_count,
                        )

                        stop_verification = (
                            self.verifier.verificate_context_with_additional_info(
                                question,
                                query_analysis,
                                self.memory,
                                self.additional_context,
                                step_count,
                                json_data,
                            )
                        )

                        self._log_llm_response(
                            "verificate_context_with_additional_info",
                            stop_verification,
                            step=step_count,
                        )
                    else:
                        self._log_llm_call(
                            "verificate_context",
                            {
                                "question": question,
                                "query_analysis": query_analysis[:200] + "...",
                                "step_count": step_count,
                            },
                            step=step_count,
                        )

                        stop_verification = self.verifier.verificate_context(
                            question,
                            image_path,
                            query_analysis,
                            self.memory,
                            step_count,
                            json_data,
                        )

                        self._log_llm_response(
                            "verificate_context", stop_verification, step=step_count
                        )

                extract_result = self.verifier.extract_conclusion(stop_verification)
                if is_pipeline_mode:
                    context_verification, conclusion, finalized_pipeline_id = (
                        extract_result
                    )
                else:
                    context_verification, conclusion = extract_result
                    finalized_pipeline_id = None

                logger.info(
                    f"[Step {step_count}] Verification conclusion: {conclusion}"
                )

                if self.verbose:
                    conclusion_emoji = "✅" if conclusion == "STOP" else "🛑"
                    print(f"\n==> 🤖 Step {step_count}: Context Verification\n")
                    print(
                        f"[Analysis]: {context_verification}\n[Conclusion]: {conclusion} {conclusion_emoji}"
                    )
                    if is_pipeline_mode and finalized_pipeline_id:
                        print(f"[Finalized Pipeline]: {finalized_pipeline_id}")
                    print(f"[Time]: {round(time.time() - local_start_time, 2)}s")

                # Break the loop if the context is verified
                if conclusion == "STOP":
                    logger.info(
                        f"Context verified - stopping execution loop at step {step_count}"
                    )

                    # In pipeline mode, finalize the selected pipeline
                    if is_pipeline_mode and finalized_pipeline_id:
                        logger.info(f"Finalizing pipeline: {finalized_pipeline_id}")
                        # Find the pipeline definition from memory
                        pipeline_def = ""
                        for action in reversed(
                            list(self.memory.get_actions().values())
                        ):
                            result = action.get("result", {})
                            if (
                                isinstance(result, dict)
                                and result.get("pipeline_id") == finalized_pipeline_id
                            ):
                                pipeline_def = result.get("pipeline", "")
                                break

                        finalize_result = self.executor.execute_tool_command(
                            "Finalize_Pipeline_Tool",
                            f'execution = tool.execute(pipeline_id="{finalized_pipeline_id}", pipeline="""{pipeline_def}""")',
                        )
                        step_count += 1
                        self.memory.add_action(
                            step_count,
                            "Finalize_Pipeline_Tool",
                            f"Mark pipeline {finalized_pipeline_id} as finalized",
                            "",
                            finalize_result,
                        )
                        self._log_memory_update(
                            step_count,
                            "Finalize_Pipeline_Tool",
                            f"Mark pipeline {finalized_pipeline_id} as finalized",
                            "",
                            finalize_result,
                        )

                        if self.verbose:
                            print(
                                f"\n==> 🏁 Pipeline '{finalized_pipeline_id}' finalized for materialization"
                            )

                    break

            # Add memory and statistics to json_data
            total_time = round(time.time() - query_start_time, 2)
            json_data.update(
                {
                    "memory": memory_actions,
                    "step_count": step_count,
                    "execution_time": total_time,
                }
            )

            logger.info(
                f"Execution loop completed - {step_count} steps in {total_time}s"
            )

            # ---- Final code extraction and verification ----
            if is_pipeline_mode:
                final_code = None

                if self.execute_pipeline:
                    # Variant 1 (With Code Execution):
                    # Tools already executed code during the loop.
                    # Extract the generated code from the finalized pipeline in memory.
                    final_code = self._get_finalized_pipeline_code(
                        finalized_pipeline_id
                    )
                    if final_code:
                        logger.info(
                            f"Extracted final code from finalized pipeline: {finalized_pipeline_id}"
                        )
                        if self.verbose:
                            print(
                                f"\n==> 📋 Using code from finalized pipeline: {finalized_pipeline_id}"
                            )
                            print(
                                f"\n==> 🐙 Final Code:\n```python\n{final_code}\n```"
                            )
                    else:
                        logger.warning(
                            f"No generated code found for finalized pipeline: {finalized_pipeline_id}"
                        )
                        if self.verbose:
                            print(
                                f"\n==> ⚠️ No code found for finalized pipeline: {finalized_pipeline_id}"
                            )
                else:
                    # Variant 2 (Without Code Execution):
                    # Generate code via LLM.
                    if "final" in self.output_types:
                        self._log_llm_call(
                            "generate_final_output",
                            {"question": question, "image_path": image_path},
                        )
                        final_output = self.planner.generate_final_output(
                            question, image_path, self.memory
                        )
                        self._log_llm_response(
                            "generate_final_output", final_output
                        )
                        json_data["final_output"] = final_output
                        final_code = self._extract_code_from_output(
                            str(final_output)
                        )
                        if self.verbose:
                            print(
                                f"\n==> 🐙 Detailed Solution:\n\n{final_output}"
                            )

                    if not final_code and "direct" in self.output_types:
                        self._log_llm_call(
                            "generate_direct_output",
                            {"question": question, "image_path": image_path},
                        )
                        direct_output = self.planner.generate_direct_output(
                            question, image_path, self.memory
                        )
                        self._log_llm_response(
                            "generate_direct_output", direct_output
                        )
                        json_data["direct_output"] = direct_output
                        final_code = self._extract_code_from_output(
                            str(direct_output)
                        )
                        if self.verbose:
                            print(
                                f"\n==> 🐙 Final Answer:\n\n{direct_output}"
                            )

                if final_code:
                    json_data["final_code"] = final_code
                    json_data["final_code_source"] = (
                        "memory" if self.execute_pipeline else "llm_generation"
                    )

                    # --- Common final step: Execute, Score, Verify ---
                    if self.ground_truth_csv:
                        if self.verbose:
                            print(
                                f"\n==> ⚙️ Executing final code and verifying results..."
                            )

                        final_exec_result = self._execute_and_score_pipeline(
                            [{"generated_code": final_code}],
                            step_count=step_count + 1,
                        )

                        if final_exec_result:
                            json_data["final_score"] = (
                                make_json_serializable_truncated(final_exec_result)
                            )
                            if self.verbose:
                                print(
                                    f"\n==> 📊 Final Score: {final_exec_result.get('score')}"
                                )

                            # Verify results using compare_lists_matching
                            if (
                                final_exec_result.get("execution_success")
                                and final_exec_result.get("output_csv_path")
                            ):
                                verification = self._verify_results(
                                    final_exec_result["output_csv_path"]
                                )
                                if verification:
                                    json_data["verification_result"] = (
                                        make_json_serializable_truncated(
                                            verification
                                        )
                                    )
                                    is_correct = verification.get(
                                        "is_correct", False
                                    )
                                    json_data["is_correct"] = is_correct
                                    if self.verbose:
                                        status = "CORRECT" if is_correct else "INCORRECT"
                                        print(
                                            f"\n==> {'✅' if is_correct else '❌'} Verification: {status}"
                                        )
                                        print(
                                            f"    Average Similarity: {verification.get('average_similarity')}"
                                        )
                                        print(
                                            f"    Matched Columns: {verification.get('all_matched_columns')}"
                                        )
                                        print(
                                            f"    Calculate Score: {verification.get('calculate_score')}"
                                        )
                            else:
                                # Execution failed or no output CSV
                                json_data["is_correct"] = False
                                if self.verbose:
                                    print(
                                        f"\n==> ❌ Verification: FAILED (no output CSV produced)"
                                    )
                    else:
                        logger.warning(
                            "No ground truth CSV available for scoring/verification"
                        )
                        json_data["is_correct"] = False
                else:
                    logger.warning(
                        "No final code available for scoring/verification"
                    )
                    json_data["is_correct"] = False

            else:
                # Non-pipeline mode: keep existing behavior
                if "final" in self.output_types:
                    self._log_llm_call(
                        "generate_final_output",
                        {"question": question, "image_path": image_path},
                    )
                    final_output = self.planner.generate_final_output(
                        question, image_path, self.memory
                    )
                    self._log_llm_response(
                        "generate_final_output", final_output
                    )
                    json_data["final_output"] = final_output
                    print(f"\n==> 🐙 Detailed Solution:\n\n{final_output}")

                if "direct" in self.output_types:
                    self._log_llm_call(
                        "generate_direct_output",
                        {"question": question, "image_path": image_path},
                    )
                    direct_output = self.planner.generate_direct_output(
                        question, image_path, self.memory
                    )
                    self._log_llm_response(
                        "generate_direct_output", direct_output
                    )
                    json_data["direct_output"] = direct_output
                    print(f"\n==> 🐙 Final Answer:\n\n{direct_output}")

            print(f"\n[Total Time]: {total_time}s")
            print(f"\n==> ✅ Query Solved!")

            logger.info("=" * 80)
            logger.info(f"Query completed successfully in {total_time}s")
            logger.info("=" * 80)

        return json_data


def construct_solver(
    llm_engine_name: str = "gpt-4.1-mini",
    enabled_tools: list[str] = ["all"],
    tool_engine: list[str] = ["Default"],
    model_engine: list[str] = ["trainable", "gpt-4o", "gpt-4o", "gpt-4o"],
    output_types: str = "final",
    max_steps: int = 10,
    max_time: int = 300,
    max_tokens: int = 4000,
    root_cache_dir: str = "solver_cache",
    verbose: bool = True,
    vllm_config_path: str = None,
    base_url: str = None,
    temperature: float = 0.0,
    additional_context_file: str = None,
    start_again_clear_history: bool = False,
    planner_granularity: str = "operator",
    execute_pipeline: bool = False,
    ground_truth_csv: str = None,
):

    logger.info("Constructing solver...")
    logger.info(f"LLM Engine: {llm_engine_name}")
    logger.info(f"Enabled Tools: {enabled_tools}")
    logger.info(f"Model Engine Config: {model_engine}")
    logger.info(f"Planner Granularity: {planner_granularity}")

    # Read additional context file if provided
    additional_context = None
    if additional_context_file:
        logger.info(f"Loading additional context from: {additional_context_file}")
        try:
            with open(additional_context_file, "r") as f:
                additional_context = f.read()
            logger.info(
                f"Additional context loaded ({len(additional_context)} characters)"
            )
        except Exception as e:
            logger.warning(f"Failed to load additional context file: {str(e)}")
            additional_context = None

    # Parse model_engine configuration
    planner_main_engine = (
        llm_engine_name if model_engine[0] == "trainable" else model_engine[0]
    )
    planner_fixed_engine = (
        llm_engine_name if model_engine[1] == "trainable" else model_engine[1]
    )
    verifier_engine = (
        llm_engine_name if model_engine[2] == "trainable" else model_engine[2]
    )
    executor_engine = (
        llm_engine_name if model_engine[3] == "trainable" else model_engine[3]
    )

    logger.info(
        f"Planner Main: {planner_main_engine}, Planner Fixed: {planner_fixed_engine}"
    )
    logger.info(f"Verifier: {verifier_engine}, Executor: {executor_engine}")

    # Instantiate Initializer
    initializer = Initializer(
        enabled_tools=enabled_tools,
        tool_engine=tool_engine,
        model_string=llm_engine_name,
        verbose=verbose,
        vllm_config_path=vllm_config_path,
    )

    # Instantiate Planner
    planner = Planner(
        llm_engine_name=planner_main_engine,
        llm_engine_fixed_name=planner_fixed_engine,
        toolbox_metadata=initializer.toolbox_metadata,
        available_tools=initializer.available_tools,
        verbose=verbose,
        base_url=base_url,
        temperature=temperature,
        granularity=planner_granularity,
        execute_pipeline=execute_pipeline,
    )

    # Instantiate Verifier
    verifier = Verifier(
        llm_engine_name=verifier_engine,
        llm_engine_fixed_name=planner_fixed_engine,
        toolbox_metadata=initializer.toolbox_metadata,
        available_tools=initializer.available_tools,
        verbose=verbose,
        base_url=base_url if verifier_engine == llm_engine_name else None,
        temperature=temperature,
        granularity=planner_granularity,
        execute_pipeline=execute_pipeline,
    )

    # Instantiate Memory
    memory = Memory()

    # Instantiate Executor with tool instances cache
    executor = Executor(
        llm_engine_name=executor_engine,
        root_cache_dir=root_cache_dir,
        verbose=verbose,
        base_url=base_url if executor_engine == llm_engine_name else None,
        temperature=temperature,
        execute_pipeline=execute_pipeline,
        tool_instances_cache=initializer.tool_instances_cache,
    )

    # Instantiate Solver
    solver = Solver(
        planner=planner,
        verifier=verifier,
        memory=memory,
        executor=executor,
        output_types=output_types,
        max_steps=max_steps,
        max_time=max_time,
        max_tokens=max_tokens,
        root_cache_dir=root_cache_dir,
        verbose=verbose,
        temperature=temperature,
        additional_context=additional_context,
        start_again_clear_history=start_again_clear_history,
        execute_pipeline=execute_pipeline,
        ground_truth_csv=ground_truth_csv,
    )

    logger.info("Solver construction completed")
    return solver


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run the agentflow demo with specified parameters."
    )
    parser.add_argument("--llm_engine_name", default="gpt-4o", help="LLM engine name.")
    parser.add_argument(
        "--output_types",
        default="base,final,direct",
        help="Comma-separated list of required outputs (base,final,direct)",
    )
    parser.add_argument(
        "--enabled_tools", default="Base_Generator_Tool", help="List of enabled tools."
    )
    parser.add_argument(
        "--root_cache_dir",
        default="solver_cache",
        help="Path to solver cache directory.",
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=4000,
        help="Maximum tokens for LLM generation.",
    )
    parser.add_argument(
        "--max_steps", type=int, default=10, help="Maximum number of steps to execute."
    )
    parser.add_argument(
        "--max_time", type=int, default=300, help="Maximum time allowed in seconds."
    )
    parser.add_argument(
        "--verbose", type=bool, default=True, help="Enable verbose output."
    )
    parser.add_argument("--log_dir", default="logs", help="Directory for log files.")
    return parser.parse_args()


def main(args):
    # Reinitialize logging with custom log directory if provided
    if hasattr(args, "log_dir"):
        global logger, component_loggers, prompt_logger, tool_logger, memory_logger
        logger, component_loggers = setup_logging(args.log_dir)
        prompt_logger = component_loggers["prompts"]
        tool_logger = component_loggers["tools"]
        memory_logger = component_loggers["memory"]

    tool_engine = ["gpt-4o-mini", "gpt-4o-mini", "Default", "Default"]
    solver = construct_solver(
        llm_engine_name=args.llm_engine_name,
        enabled_tools=[
            "Base_Generator_Tool",
            "Python_Coder_Tool",
            "Google_Search_Tool",
            "Wikipedia_Search_Tool",
        ],
        tool_engine=tool_engine,
        output_types=args.output_types,
        max_steps=args.max_steps,
        max_time=args.max_time,
        max_tokens=args.max_tokens,
        # base_url="http://localhost:8080/v1",
        verbose=args.verbose,
        temperature=0.7,
    )

    # Solve the task or problem
    solver.solve("What is the capital of France?")

    logger.info("Main execution completed")
    print(
        f"\n📝 Logs saved to: {args.log_dir if hasattr(args, 'log_dir') else 'logs'}/"
    )


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
