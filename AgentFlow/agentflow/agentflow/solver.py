import argparse
import time
import json
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from agentflow.models.initializer import Initializer
from agentflow.models.planner import Planner
from agentflow.models.verifier import Verifier
from agentflow.models.memory import Memory
from agentflow.models.executor import Executor
from agentflow.models.utils import make_json_serializable_truncated


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

        self.output_types = output_types.lower().split(",")
        self.temperature = temperature
        assert all(
            output_type in ["base", "final", "direct"]
            for output_type in self.output_types
        ), "Invalid output type. Supported types are 'base', 'final', 'direct'."
        self.verbose = verbose

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
                                "additional_context": self.additional_context[:200] + "...",
                                "step_count": step_count,
                            },
                            step=step_count,
                        )

                        stop_verification = (
                            self.verifier.verificate_context_pipeline_with_additional_info(
                                question,
                                query_analysis,
                                self.memory,
                                self.additional_context,
                                step_count,
                                json_data,
                            )
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
                            "verificate_context_pipeline", stop_verification, step=step_count
                        )
                else:
                    # Operator-level verification (original behavior)
                    if self.additional_context:
                        self._log_llm_call(
                            "verificate_context_with_additional_info",
                            {
                                "question": question,
                                "query_analysis": query_analysis[:200] + "...",
                                "additional_context": self.additional_context[:200] + "...",
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
                    context_verification, conclusion, finalized_pipeline_id = extract_result
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
                        logger.info(
                            f"Finalizing pipeline: {finalized_pipeline_id}"
                        )
                        # Find the pipeline definition from memory
                        pipeline_def = ""
                        for action in reversed(list(self.memory.get_actions().values())):
                            result = action.get("result", {})
                            if isinstance(result, dict) and result.get("pipeline_id") == finalized_pipeline_id:
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
                            step_count, "Finalize_Pipeline_Tool",
                            f"Mark pipeline {finalized_pipeline_id} as finalized",
                            "", finalize_result,
                        )

                        if self.verbose:
                            print(f"\n==> 🏁 Pipeline '{finalized_pipeline_id}' finalized for materialization")

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

            # Generate final output if requested
            if "final" in self.output_types:
                self._log_llm_call(
                    "generate_final_output",
                    {"question": question, "image_path": image_path},
                )

                final_output = self.planner.generate_final_output(
                    question, image_path, self.memory
                )

                self._log_llm_response("generate_final_output", final_output)
                json_data["final_output"] = final_output

                print(f"\n==> 🐙 Detailed Solution:\n\n{final_output}")

            # Generate direct output if requested
            if "direct" in self.output_types:
                self._log_llm_call(
                    "generate_direct_output",
                    {"question": question, "image_path": image_path},
                )

                direct_output = self.planner.generate_direct_output(
                    question, image_path, self.memory
                )

                self._log_llm_response("generate_direct_output", direct_output)
                json_data["direct_output"] = direct_output

                print(f"\n==> 🐙 Final Answer:\n\n{direct_output}")

            print(f"\n[Total Time]: {total_time}s")
            print(f"\n==> ✅ Query Solved!")

            logger.info("=" * 80)
            logger.info(f"Query completed successfully in {total_time}s")
            logger.info("=" * 80)

        return json_data


def construct_solver(
    llm_engine_name: str = "gpt-4o",
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
