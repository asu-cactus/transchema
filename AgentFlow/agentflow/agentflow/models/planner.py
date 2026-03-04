import json
import os
import re
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image

from agentflow.engine.factory import create_llm_engine
from agentflow.models.formatters import NextStep, QueryAnalysis
from agentflow.models.memory import Memory

_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[4])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)
from hints.hints_static import get_hints_section, NEXT_OPERATOR_HINT_IDS

# Get the prompt logger
prompt_logger = logging.getLogger("agentflow.prompts")


class Planner:
    def __init__(
        self,
        llm_engine_name: str,
        llm_engine_fixed_name: str = "gpt-4.1-mini",
        toolbox_metadata: dict = None,
        available_tools: List = None,
        verbose: bool = False,
        base_url: str = None,
        is_multimodal: bool = False,
        check_model: bool = True,
        temperature: float = 0.0,
        granularity: str = "operator",
        execute_pipeline: bool = False,
    ):
        self.llm_engine_name = llm_engine_name
        self.llm_engine_fixed_name = llm_engine_fixed_name
        self.is_multimodal = is_multimodal
        self.granularity = granularity
        self.execute_pipeline = execute_pipeline
        # self.llm_engine_mm = create_llm_engine(model_string=llm_engine_name, is_multimodal=False, base_url=base_url, temperature = temperature)
        self.llm_engine_fixed = create_llm_engine(
            model_string=llm_engine_fixed_name,
            is_multimodal=False,
            temperature=temperature,
        )
        self.llm_engine = create_llm_engine(
            model_string=llm_engine_name,
            is_multimodal=False,
            base_url=base_url,
            temperature=temperature,
        )
        self.toolbox_metadata = toolbox_metadata if toolbox_metadata is not None else {}
        self.available_tools = available_tools if available_tools is not None else []

        self.verbose = verbose

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        image_info = {}
        if image_path and os.path.isfile(image_path):
            image_info["image_path"] = image_path
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                image_info.update({"width": width, "height": height})
            except Exception as e:
                print(f"Error processing image file: {str(e)}")
        return image_info

    def generate_base_response(
        self, question: str, image: str, max_tokens: int = 2048
    ) -> str:
        image_info = self.get_image_info(image)

        input_data = [question]
        if image_info and "image_path" in image_info:
            try:
                with open(image_info["image_path"], "rb") as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                print(f"Error reading image file: {str(e)}")

        print("Input data of `generate_base_response()`: ", input_data)

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("GENERATE_BASE_RESPONSE PROMPT:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(f"Question: {question}")
        if image_info:
            prompt_logger.debug(f"Image Info: {image_info}")
        prompt_logger.debug("=" * 80)

        self.base_response = self.llm_engine(input_data, max_tokens=max_tokens)
        # self.base_response = self.llm_engine_fixed(input_data, max_tokens=max_tokens)

        return self.base_response

    def analyze_query(self, question: str, image: str) -> str:
        if self.granularity == "pipeline":
            return self._analyze_query_pipeline(question, image)
        return self._analyze_query_operator(question, image)

    def _analyze_query_pipeline(self, question: str, image: str) -> str:
        image_info = self.get_image_info(image)

        query_prompt = f"""
Task: Analyze the given query at a PIPELINE level to determine whether a new data transformation pipeline needs to be created or an existing pipeline should be modified.

CRITICAL CONSTRAINT: You can ONLY suggest operations and tools that are in the available tools list. Do NOT suggest operations or tools that are not available.

Inputs:
- Query: {question}
- Available tools: {self.available_tools}
- Metadata for tools: {self.toolbox_metadata}

Instructions:
1. Understand the high-level goal of the query — what is the desired end-to-end data transformation?
2. Determine whether this requires:
   a) Creating a NEW pipeline from scratch (no existing pipeline addresses this transformation), or
   b) Modifying an EXISTING pipeline (the transformation is partially addressed and needs adjustments).
3. Choose the operation sequence to build the target table: which joins, unions, aggregations, etc. steps to apply, in what order.
4. List ONLY the skills and tools that are actually available in the available tools list.
5. Note any additional considerations at the pipeline level.

Format your response with:
- A concise summary of the query and the target transformation
- Pipeline decision: CREATE NEW or MODIFY EXISTING (and why)
- Required skills and relevant tools from the available list
- Additional considerations

IMPORTANT: Be brief and precise. Focus on the pipeline-level strategy, NOT individual operator details.
"""

        input_data = [query_prompt]
        if image_info:
            try:
                with open(image_info["image_path"], "rb") as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                print(f"Error reading image file: {str(e)}")

        print("Input data of `analyze_query() [pipeline-level]`: ", input_data)

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("ANALYZE_QUERY PROMPT [PIPELINE-LEVEL]:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(query_prompt)
        prompt_logger.debug("=" * 80)

        self.query_analysis = self.llm_engine_fixed(
            input_data, response_format=QueryAnalysis
        )

        return str(self.query_analysis).strip()

    def _analyze_query_operator(self, question: str, image: str) -> str:
        image_info = self.get_image_info(image)

        if self.is_multimodal:
            query_prompt = f"""
Task: Analyze the given query to determine necessary skills and tools.

CRITICAL CONSTRAINT: You can ONLY suggest operations and tools that are in the available tools list. Do NOT suggest operations or tools that are not available.

Inputs:
- Query: {question}
- Available tools: {self.available_tools}
- Metadata for tools: {self.toolbox_metadata}

Instructions:
1. Identify the main objectives in the query.
2. List ONLY the skills and tools that are actually available in the available tools list.
3. For each skill and tool, explain how it helps address the query.
4. If the query requires operations not supported by available tools, explicitly note this limitation.
5. Note any additional considerations.

Format your response with a summary of the query, lists of skills and tools with explanations, and a section for additional considerations.

IMPORTANT: Be brief and precise. Focus ONLY on what can be achieved with the available tools.

                        """
        else:
            query_prompt = f"""
Task: Analyze the given query to determine necessary skills and tools.

CRITICAL CONSTRAINT: You can ONLY suggest operations and tools that are in the available tools list. Do NOT suggest operations or tools that are not available.

Inputs:
- Query: {question}
- Available tools: {self.available_tools}
- Metadata for tools: {self.toolbox_metadata}

Instructions:
1. Identify the main objectives in the query.
2. List ONLY the skills and tools that are actually available in the available tools list.
3. For each skill and tool, explain how it helps address the query.
4. If the query requires operations not supported by available tools, explicitly note this limitation.
5. Note any additional considerations.

Format your response with a summary of the query, lists of skills and tools with explanations, and a section for additional considerations.

IMPORTANT: Be brief and precise. Focus ONLY on what can be achieved with the available tools.
"""

        input_data = [query_prompt]
        if image_info:
            try:
                with open(image_info["image_path"], "rb") as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                print(f"Error reading image file: {str(e)}")

        print("Input data of `analyze_query()`: ", input_data)

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("ANALYZE_QUERY PROMPT:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(query_prompt)
        prompt_logger.debug("=" * 80)

        # self.query_analysis = self.llm_engine_mm(input_data, response_format=QueryAnalysis)
        # self.query_analysis = self.llm_engine(input_data, response_format=QueryAnalysis)
        self.query_analysis = self.llm_engine_fixed(
            input_data, response_format=QueryAnalysis
        )

        return str(self.query_analysis).strip()

    def extract_context_subgoal_and_tool(self, response: Any) -> Tuple[str, str, str]:

        def normalize_tool_name(tool_name: str) -> str:
            """
            Normalizes a tool name robustly using regular expressions.
            It handles any combination of spaces and underscores as separators.
            """

            def to_canonical(name: str) -> str:
                # Split the name by any sequence of one or more spaces or underscores
                parts = re.split("[ _]+", name)
                # Join the parts with a single underscore and convert to lowercase
                return "_".join(part.lower() for part in parts)

            normalized_input = to_canonical(tool_name)

            for tool in self.available_tools:
                if to_canonical(tool) == normalized_input:
                    return tool

            return f"No matched tool given: {tool_name}"

        try:
            if isinstance(response, str):
                # Attempt to parse the response as JSON
                try:
                    response_dict = json.loads(response)
                    response = NextStep(**response_dict)
                except Exception as e:
                    print(f"Failed to parse response as JSON: {str(e)}")
            if isinstance(response, NextStep):
                print("arielg 1")
                context = response.context.strip()
                sub_goal = response.sub_goal.strip()
                tool_name = response.tool_name.strip()
            else:
                print("arielg 2")
                text = response.replace("**", "")

                # Pattern to match the exact format
                pattern = r"Context:\s*(.*?)Sub-Goal:\s*(.*?)Tool Name:\s*(.*?)\s*(?:```)?\s*(?=\n\n|\Z)"

                # Find all matches
                matches = re.findall(pattern, text, re.DOTALL)

                # Return the last match (most recent/relevant)
                context, sub_goal, tool_name = matches[-1]
                context = context.strip()
                sub_goal = sub_goal.strip()
            tool_name = normalize_tool_name(tool_name)
        except Exception as e:
            print(f"Error extracting context, sub-goal, and tool name: {str(e)}")
            return None, None, None

        return context, sub_goal, tool_name

    def generate_next_step(
        self,
        question: str,
        image: str,
        query_analysis: str,
        memory: Memory,
        step_count: int,
        max_step_count: int,
        json_data: Any = None,
    ) -> Any:
        if self.granularity == "pipeline":
            return self._generate_next_step_pipeline(
                question,
                image,
                query_analysis,
                memory,
                step_count,
                max_step_count,
                json_data,
            )
        return self._generate_next_step_operator(
            question,
            image,
            query_analysis,
            memory,
            step_count,
            max_step_count,
            json_data,
        )

    def _generate_next_step_pipeline(
        self,
        question: str,
        image: str,
        query_analysis: str,
        memory: Memory,
        step_count: int,
        max_step_count: int,
        json_data: Any = None,
    ) -> Any:
        # Build score feedback section only when execute_pipeline is enabled
        if self.execute_pipeline:
            score_feedback_section = """
5. **Score Understanding**: When a previous step result includes a `score_summary`, use it to determine whether to continue refining or finalize. The score measures how well the generated output matches the target across three components:

   - **Functional Dependency Matching** (`functional_dependency_f1_score`): A functional dependency is a data constraint where one column determines another. If `score_summary.functional_dependencies.missed` is non-empty, the output is missing grouping constraints. Fix: add a GROUP BY using the key columns from the target with appropriate aggregations at the end of the pipeline.

   - **Key Matching** (`score_summary.keys.missed_ground_truth_keys`): Keys are column sets that uniquely identify each row. If `missed_ground_truth_keys` is non-empty, the output has duplicate rows or wrong grouping. Fix: add a GROUP BY on the columns listed in `missed_ground_truth_keys` with appropriate aggregations.

   - **Column Mapping** (`score_summary.column_mappings.missed_target_columns`): If `missed_target_columns` is non-empty, those columns are absent from the output. Fix: add JOINs with the source tables that contain those missing columns.

   - The pipeline is complete ONLY when all three are satisfied: overall_score = 1.0, no missed functional dependencies, no missed ground truth keys, no missed target columns.

   - If execution_error is present, the generated code has bugs — modify the pipeline or regenerate the code.
   - If the pipeline has joins and row counts are wrong, try changing join types (inner to left or left to inner).
   - If the score is not improving across iterations, consider Start_Again_Tool.

6. Formulate a specific, achievable **sub-goal** for the selected tool.
7. Provide all necessary **context** (data, file names, variables) for the tool to function."""
            # code_gen_description = "**Code_Generator_Tool**: Use to generate executable Python code that materializes the pipeline. The code will be automatically executed and scored against the ground truth. Use when you want to test whether the current pipeline produces the correct output or when you need score feedback to decide what to fix next."
            extra_reasoning = ""
        else:
            score_feedback_section = """
5. Formulate a specific, achievable **sub-goal** for the selected tool.
6. Provide all necessary **context** (data, file snames, variables) for the tool to function."""
            # code_gen_description = "**Code_Generator_Tool**: Use to visualize the current pipeline state. Generates executable Python code that materializes operations configured so far. Use when you need to verify the pipeline's combined effect before proceeding."
            extra_reasoning = ""

        prompt_generate_next_step = f"""
Task: Determine the optimal next step at a PIPELINE level to address the given query.

You are operating at a PIPELINE granularity. Instead of picking individual operators one at a time, you should reason about the pipeline as a whole and decide whether to:
1. **Create a new pipeline** — Design the full sequence of operations needed to achieve the target transformation.
2. **Modify the existing pipeline** — Adjust, add, remove, or reconfigure operations in the current pipeline to fix issues or improve correctness.

CRITICAL CONSTRAINT: You can ONLY use tools from the available tools list. Do NOT suggest operations, sub-goals, or actions that require tools not in this list.

Context:
- **Query:** {question}
- **Query Analysis:** {query_analysis}
- **Available Tools (THESE ARE THE ONLY TOOLS YOU CAN USE):** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Current Step:** {step_count} of {max_step_count}
- **Remaining Steps:** {max_step_count - step_count}
- **Previous Steps and Their Results:** {memory.get_actions()}

Instructions:
1. Review the query, the pipeline-level analysis, and all previous steps.
2. Decide the pipeline-level action:
   - If a pipeline is in progress, evaluate whether it is on track or needs refinement.
3. Select the **single best tool** from the available tools list for the next step.
{score_feedback_section}

Pipeline-Level Reasoning:
- Plan the end-to-end transformation from sources to target.
- Consider the overall pipeline structure: what operations are needed, in what order, and how they connect.
- When creating a new pipeline, plan the full sequence.
- When modifying, identify exactly what is wrong and what change will fix it.{extra_reasoning}

Response Format:
1. **Justification:** Explain your pipeline-level reasoning and choice of tool.
2. **Context:** Provide all necessary information for the tool.
3. **Sub-Goal:** State the specific objective for the tool.
4. **Tool Name:** State the exact name of the selected tool (must be from available tools list).

Rules:
- Select only ONE tool from the available tools list.
- The sub-goal must be directly achievable by the selected tool.
- The response must end with the Context, Sub-Goal, and Tool Name sections in that order, with no extra content.
"""
        # Removed Operation History

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(
            f"GENERATE_NEXT_STEP PROMPT [PIPELINE-LEVEL] (Step {step_count}):"
        )
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_generate_next_step)
        prompt_logger.debug("=" * 80)

        next_step = self.llm_engine(prompt_generate_next_step, response_format=NextStep)
        if json_data is not None:
            json_data[f"action_predictor_{step_count}_prompt"] = (
                prompt_generate_next_step
            )
            json_data[f"action_predictor_{step_count}_response"] = str(next_step)
        return next_step

    def _generate_next_step_operator(
        self,
        question: str,
        image: str,
        query_analysis: str,
        memory: Memory,
        step_count: int,
        max_step_count: int,
        json_data: Any = None,
    ) -> Any:
        if self.is_multimodal:
            prompt_generate_next_step = f"""
Task: Determine the optimal next step to address the given query based on the provided analysis, available tools, and previous steps taken.

CRITICAL CONSTRAINT: You can ONLY use tools from the available tools list. Do NOT suggest operations, sub-goals, or actions that require tools not in this list.

Context:
Query: {question}
Image: {image}
Query Analysis: {query_analysis}

Available Tools (THESE ARE THE ONLY TOOLS YOU CAN USE):
{self.available_tools}

Tool Metadata:
{self.toolbox_metadata}

Previous Steps and Their Results:
{memory.get_actions()}

Current Step: {step_count} in {max_step_count} steps
Remaining Steps: {max_step_count - step_count}

Instructions:
1. Analyze the context thoroughly, including the query, its analysis, any image, available tools and their metadata, and previous steps taken.

2. Determine the most appropriate next step by considering:
- Key objectives from the query analysis
- Capabilities of ONLY the available tools (do not assume any other tools exist)
- Logical progression of problem-solving within the scope of available tools
- Outcomes from previous steps
- Current step count and remaining steps

3. Select ONE tool from the available tools list that is best suited for the next step.
   Consider these special tools if available:
   - **Code_Generator_Tool**: Use this tool when you need to visualize or score the current pipeline state (i.e., the accumulated operations in memory). It generates executable Python code that materializes the transformation operations configured so far, allowing you to understand what the data looks like after those transformations. Use it when:
     * You are NOT confident about what operator to add next and need to see the intermediate data to make a better decision.
     * Multiple operations have been configured and you need to verify their combined effect before proceeding.
     * You want to understand the shape, schema, or content of the data after the transformations performed so far.
     Do NOT use the Code_Generator_Tool if you are already confident about the next operator to add — in that case, proceed directly with the appropriate Configure or Add tool.

4. Formulate a specific, achievable sub-goal for the selected tool that:
   - Is directly achievable with that specific tool's capabilities
   - Does NOT require operations outside the scope of available tools
   - Maximizes progress towards answering the query within tool constraints

Response Format:
Your response MUST follow this structure:
1. Justification: Explain your choice in detail.
2. Context, Sub-Goal, and Tool: Present the context, sub-goal, and the selected tool ONCE with the following format:

Context: <context>
Sub-Goal: <sub_goal>
Tool Name: <tool_name>

Where:
- <context> MUST include ALL necessary information for the tool to function, structured as follows:
* Relevant data from previous steps
* File names or paths created or used in previous steps (list EACH ONE individually)
* Variable names and their values from previous steps' results
* Any other context-specific information required by the tool
- <sub_goal> is a specific, achievable objective for the tool, based on its metadata and previous outcomes.
It MUST contain any involved data, file names, and variables from Previous Steps and Their Results that the tool can act upon.
- <tool_name> MUST be the exact name of a tool from the available tools list.

Rules:
- Select only ONE tool for this step from the available tools list.
- The sub-goal MUST be directly achievable by the selected tool using ONLY its documented capabilities.
- Do NOT suggest sub-goals that require operations or transformations not supported by available tools.
- The Context section MUST include ALL necessary information for the tool to function, including ALL relevant file paths, data, and variables from previous steps.
- The tool name MUST exactly match one from the available tools list: {self.available_tools}.
- If the next logical step requires a tool not in the available tools list, you MUST either:
  a) Choose an alternative approach using available tools, OR
  b) Indicate that no more steps can be taken with available tools
- Avoid redundancy by considering previous steps and building on prior results.
- Your response MUST conclude with the Context, Sub-Goal, and Tool Name sections IN THIS ORDER, presented ONLY ONCE.
- Include NO content after these three sections.

Example (do not copy, use only as reference):
Justification: [Your detailed explanation here]
Context: Image path: "example/image.jpg", Previous detection results: [list of objects]
Sub-Goal: Detect and count the number of specific objects in the image "example/image.jpg"
Tool Name: Object_Detector_Tool

Remember: Your response MUST end with the Context, Sub-Goal, and Tool Name sections, with NO additional content afterwards.
                        """
        else:
            # Build score feedback section (operator mode, mirroring pipeline mode guidance)
            if self.execute_pipeline:
                score_feedback_section = """
**Score Feedback** — When a previous step contains a `score_summary` from `Code_Gen_And_Score_Tool`, use it to guide the next action:
- `score = 1.0` AND no missed items in any category → pipeline is complete, do NOT add more operators.
- `functional_dependencies.missed` is non-empty → add or fix a GROUP BY operator.
- `keys.missed_ground_truth_keys` is non-empty → add GROUP BY on those columns.
- `column_mappings.missed_target_columns` is non-empty → add a JOIN to source tables that contain those columns.
- Code execution failed (`execution_success = False`) → invoke `Critique_Pipeline_Tool` to diagnose and suggest corrections.
- Score improved but is still < 1.0 → inspect the `score_summary` to determine which category needs fixing and choose the appropriate operator tool.
"""
            else:
                score_feedback_section = ""

            prompt_generate_next_step = f"""
Task: Determine the optimal next step to build the data transformation pipeline operator by operator.

You are operating at OPERATOR granularity. You configure one operator at a time, incrementally building the pipeline. Each tool below corresponds to a specific operator or a utility action.

CRITICAL CONSTRAINT: You can ONLY use tools from the available tools list. Do NOT suggest operations or tools that are not in this list.

=== OPERATOR TOOLS (configure one operator per step) ===
- **Configure_Join_Operator_Tool**: Configure a JOIN between two tables. Use when the target columns span multiple source tables that share a key column (primary key / foreign key relationship), or when different schemas need to be combined on a common attribute.
- **Configure_Union_Operator_Tool**: Configure a UNION (stack) of tables with identical schemas. Use when multiple source tables have the same columns and their rows need to be combined into one table.
- **Configure_GroupBy_Aggregate_Operator_Tool**: Configure GROUP BY + aggregation. Use when the target has fewer rows than the source (i.e., rows need to be rolled up), or when target columns have aggregated values (sum, count, avg, etc.).
- **Add_Pivot_Tool**: Configure a PIVOT operation to turn row values into column headers (wide format). Use when distinct values from one source column should become separate columns in the target.
- **Add_Unpivot_Tool**: Configure an UNPIVOT (melt) operation to turn column headers into row values (narrow format). Use when multiple source columns should be stacked into rows with a key-value structure.

=== UTILITY TOOLS (use strategically, not at every step) ===
- **Code_Gen_And_Score_Tool**: Generate Python code implementing all operators configured so far, execute it, and calculate the score against the target table. Use this tool when:
  * You believe the pipeline is complete (all needed operators are configured) — to verify the result.
  * You need to materialize intermediate results to understand the current data shape before deciding the next operator.
  After invocation, the `score_summary` in the result tells you exactly what is correct and what still needs fixing.
- **Critique_Pipeline_Tool**: Critique the current pipeline and suggest specific corrections. Use this tool when:
  * `Code_Gen_And_Score_Tool` produced a low score and you need structured analysis of what went wrong.
  * The verifier flagged issues and you need expert guidance on which operators to add, change, or remove.
  * The pipeline is close to correct but 1-2 operators need adjustment.

{score_feedback_section}
=== DOMAIN HINTS FOR OPERATOR SELECTION ===
{get_hints_section(NEXT_OPERATOR_HINT_IDS, fmt="bullet")}

Context:
- **Query:** {question}
- **Query Analysis:** {query_analysis}
- **Available Tools (THESE ARE THE ONLY TOOLS YOU CAN USE):** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Previous Steps and Their Results:** {memory.get_actions()}
- **Current Step:** {step_count} of {max_step_count}
- **Remaining Steps:** {max_step_count - step_count}

Instructions:
1. Review the query, schemas, previous steps, and any score feedback.
2. Determine which operator to configure next, OR whether to generate/score code, OR whether to critique.
3. Select the **single best tool** for this step.
4. Formulate a specific, achievable **sub-goal** directly achievable by that tool.
5. Provide all necessary **context** (source/target schemas, file paths, operation history, error messages).

Response Format:
1. **Justification:** Explain your reasoning and choice of tool.
2. **Context:** All information the tool needs (schemas, examples, file paths, prior operator results).
3. **Sub-Goal:** The specific objective for the selected tool.
4. **Tool Name:** The exact name from the available tools list.

Rules:
- Select only ONE tool from the available tools list.
- The sub-goal must be directly achievable by the selected tool.
- The response must end with the Context, Sub-Goal, and Tool Name sections in that order, with no extra content.
                    """

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(f"GENERATE_NEXT_STEP PROMPT (Step {step_count}):")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_generate_next_step)
        prompt_logger.debug("=" * 80)

        next_step = self.llm_engine(prompt_generate_next_step, response_format=NextStep)
        if json_data is not None:
            json_data[f"action_predictor_{step_count}_prompt"] = (
                prompt_generate_next_step
            )
            json_data[f"action_predictor_{step_count}_response"] = str(next_step)
        return next_step

    def generate_final_output(self, question: str, image: str, memory: Memory) -> str:
        if self.granularity == "pipeline":
            return self._generate_final_output_pipeline(question, image, memory)
        return self._generate_final_output_operator(question, image, memory)

    def _generate_final_output_pipeline(
        self, question: str, image: str, memory: Memory
    ) -> str:
        """Generate a Python script as the final output for pipeline-level granularity."""
        # Extract the finalized pipeline from memory
        finalized_pipeline = ""
        finalized_pipeline_id = ""
        for action in reversed(list(memory.get_actions().values())):
            result = action.get("result", {})
            if (
                isinstance(result, dict)
                and result.get("signal") == "PIPELINE_FINALIZED"
            ):
                finalized_pipeline_id = result.get("pipeline_id", "")
                finalized_pipeline = result.get("pipeline", "")
                break

        prompt = f"""You are generating executable Python code at runtime. A data transformation pipeline has been designed and finalized. Your job is to translate this pipeline into a complete, executable Python script using pandas.

Transformation Context:
{question}

Finalized Pipeline (ID: {finalized_pipeline_id}):
{finalized_pipeline}

Full Action History (for reference):
{memory.get_actions()}

Instructions:
1. Generate a complete Python script that implements the finalized pipeline.
2. The script must be immediately executable — no placeholders, no omissions.
3. Follow the pipeline's sequence of operations strictly.
4. Use pandas for all data transformations.
5. Read all source CSV files as specified in the query (use index_col=0 since most source files have a numerical index column).
6. Ensure the output matches the target schema exactly (column names, types, order).
7. Save the final result to a CSV file.

Key guidelines:
- All source tables must be used.
- For JOIN operations: use pd.merge() with appropriate join keys and join type (inner/outer).
- For UNION operations: use pd.concat() on tables with compatible schemas.
- For GROUP_BY/AGGREGATE: use .groupby() with .agg().
- GROUP BY columns are never float types — they correspond to unique, non-float columns at the leftmost part of the target schema.
- If target examples contain duplicate keys or rows, GROUP BY should NOT be used.
- Two tables may join on columns with different names but similar values.
- Most source files have a numerical index column (first column) — use index_col=0 when reading.
- Ensure the final output has the same column structure as the target table.

Please quote the Python script between one single "```Python" and "```".
"""

        input_data = [prompt]

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("GENERATE_FINAL_OUTPUT PROMPT [PIPELINE-LEVEL]:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt)
        prompt_logger.debug("=" * 80)

        final_output = self.llm_engine_fixed(input_data)

        return final_output

    def _generate_final_output_operator(
        self, question: str, image: str, memory: Memory
    ) -> str:
        image_info = self.get_image_info(image)
        if self.is_multimodal:
            prompt_generate_final_output = f"""
Task: Generate the final output based on the query, image, and tools used in the process.

Context:
Query: {question}
Image: {image_info}
Actions Taken:
{memory.get_actions()}

Instructions:
1. Review the query, image, and all actions taken during the process.
2. Consider the results obtained from each tool execution.
3. Incorporate the relevant information from the memory to generate the step-by-step final output.
4. The final output should be consistent and coherent using the results from the tools.

Output Structure:
Your response should be well-organized and include the following sections:

1. Summary:
   - Provide a brief overview of the query and the main findings.

2. Detailed Analysis:
   - Break down the process of answering the query step-by-step.
   - For each step, mention the tool used, its purpose, and the key results obtained.
   - Explain how each step contributed to addressing the query.

3. Key Findings:
   - List the most important discoveries or insights gained from the analysis.
   - Highlight any unexpected or particularly interesting results.

4. Answer to the Query:
   - Directly address the original question with a clear and concise answer.
   - If the query has multiple parts, ensure each part is answered separately.

5. Additional Insights (if applicable):
   - Provide any relevant information or insights that go beyond the direct answer to the query.
   - Discuss any limitations or areas of uncertainty in the analysis.

6. Conclusion:
   - Summarize the main points and reinforce the answer to the query.
   - If appropriate, suggest potential next steps or areas for further investigation.
"""
        else:
            prompt_generate_final_output = f"""
Task: Generate the final output based on the query and the results from all tools used.

Context:
- **Query:** {question}
- **Actions Taken:** {memory.get_actions()}

Instructions:
1. Review the query and the results from all tool executions.
2. Incorporate the relevant information to create a coherent, step-by-step final output.
"""

        input_data = [prompt_generate_final_output]
        if image_info:
            try:
                with open(image_info["image_path"], "rb") as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                print(f"Error reading image file: {str(e)}")

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("GENERATE_FINAL_OUTPUT PROMPT:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_generate_final_output)
        prompt_logger.debug("=" * 80)

        # final_output = self.llm_engine_mm(input_data)
        # final_output = self.llm_engine(input_data)
        final_output = self.llm_engine_fixed(input_data)

        return final_output

    def generate_direct_output(self, question: str, image: str, memory: Memory) -> str:
        if self.granularity == "pipeline":
            return self._generate_direct_output_pipeline(question, image, memory)
        return self._generate_direct_output_operator(question, image, memory)

    def _generate_direct_output_pipeline(
        self, question: str, image: str, memory: Memory
    ) -> str:
        """Generate a Python script as the direct output for pipeline-level granularity."""
        # Extract the finalized pipeline from memory
        finalized_pipeline = ""
        finalized_pipeline_id = ""
        for action in reversed(list(memory.get_actions().values())):
            result = action.get("result", {})
            if (
                isinstance(result, dict)
                and result.get("signal") == "PIPELINE_FINALIZED"
            ):
                finalized_pipeline_id = result.get("pipeline_id", "")
                finalized_pipeline = result.get("pipeline", "")
                break

        prompt = f"""You are generating executable Python code at runtime. Translate the finalized data transformation pipeline into a complete, executable Python script.

Transformation Context:
{question}

Initial Analysis:
{self.query_analysis}

Finalized Pipeline (ID: {finalized_pipeline_id}):
{finalized_pipeline}

Action History:
{memory.get_actions()}

Generate a complete, immediately executable Python script using pandas that:
1. Reads all source CSV files (use index_col=0).
2. Implements every operation in the finalized pipeline in order.
3. Produces output matching the target schema exactly (column names, types, order).
4. Saves the result to a CSV file.

Rules:
- All source tables must be used.
- JOIN → pd.merge(); UNION → pd.concat(); GROUP_BY/AGGREGATE → .groupby().agg().
- No placeholders or omissions — the script must be complete.

Please quote the Python script between one single "```Python" and "```".
"""

        input_data = [prompt]

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("GENERATE_DIRECT_OUTPUT PROMPT [PIPELINE-LEVEL]:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt)
        prompt_logger.debug("=" * 80)

        final_output = self.llm_engine_fixed(input_data)

        return final_output

    def _generate_direct_output_operator(
        self, question: str, image: str, memory: Memory
    ) -> str:
        image_info = self.get_image_info(image)
        if self.is_multimodal:
            prompt_generate_final_output = f"""
Context:
Query: {question}
Image: {image_info}
Initial Analysis:
{self.query_analysis}
Actions Taken:
{memory.get_actions()}

Please generate the concise output based on the query, image information, initial analysis, and actions taken. Break down the process into clear, logical, and conherent steps. Conclude with a precise and direct answer to the query.

Answer:
"""
        else:
            prompt_generate_final_output = f"""
Task: Generate a concise final answer to the query based on all provided context.

Context:
- **Query:** {question}
- **Initial Analysis:** {self.query_analysis}
- **Actions Taken:** {memory.get_actions()}

Instructions:
1. Review the query and the results from all actions.
2. Synthesize the key findings into a clear, step-by-step summary of the process.
3. Provide a direct, precise answer to the original query.

Output Structure:
1.  **Process Summary:** A clear, step-by-step breakdown of how the query was addressed, including the purpose and key results of each action.
2.  **Answer:** A direct and concise final answer to the query.
"""

        input_data = [prompt_generate_final_output]
        if image_info:
            try:
                with open(image_info["image_path"], "rb") as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                print(f"Error reading image file: {str(e)}")

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug("GENERATE_DIRECT_OUTPUT PROMPT:")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_generate_final_output)
        prompt_logger.debug("=" * 80)

        # final_output = self.llm_engine(input_data)
        final_output = self.llm_engine_fixed(input_data)
        # final_output = self.llm_engine_mm(input_data)

        return final_output
