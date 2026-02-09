import json
import os
import re
import logging
from typing import Any, Dict, List, Tuple

from PIL import Image

from agentflow.engine.factory import create_llm_engine
from agentflow.models.formatters import NextStep, QueryAnalysis
from agentflow.models.memory import Memory

# Get the prompt logger
prompt_logger = logging.getLogger("agentflow.prompts")


class Planner:
    def __init__(
        self,
        llm_engine_name: str,
        llm_engine_fixed_name: str = "gpt-4o",
        toolbox_metadata: dict = None,
        available_tools: List = None,
        verbose: bool = False,
        base_url: str = None,
        is_multimodal: bool = False,
        check_model: bool = True,
        temperature: float = 0.0,
    ):
        self.llm_engine_name = llm_engine_name
        self.llm_engine_fixed_name = llm_engine_fixed_name
        self.is_multimodal = is_multimodal
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
        prompt_logger.debug("="*80)
        prompt_logger.debug("GENERATE_BASE_RESPONSE PROMPT:")
        prompt_logger.debug("="*80)
        prompt_logger.debug(f"Question: {question}")
        if image_info:
            prompt_logger.debug(f"Image Info: {image_info}")
        prompt_logger.debug("="*80)

        self.base_response = self.llm_engine(input_data, max_tokens=max_tokens)
        # self.base_response = self.llm_engine_fixed(input_data, max_tokens=max_tokens)

        return self.base_response

    def analyze_query(self, question: str, image: str) -> str:
        image_info = self.get_image_info(image)

        if self.is_multimodal:
            query_prompt = f"""
You are a PLANNER for an LLM-based data transformation system.

Your job: decide the NEXT ACTION to build a transformation pipeline that maps the given source table(s) to the target table.

You must choose exactly ONE of these decisions:
- ADD_OPERATOR  (meaning: add a new operator to the pipeline)
- NO_MORE_OPERATOR (meaning: the pipeline is complete enough; stop adding operators)

If you choose ADD_OPERATOR, you must also choose an operator type from:
['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT'].

You have access to tools. Your final output MUST be a JSON object with exactly:
\{
  "context": "...",
  "sub_goal": "...",
  "tool_name": "..."
}
Where tool_name MUST match exactly one of the available tools.

--------------------
TRANSFORMATION CASE
--------------------
{question}

--------------------
TOOLS YOU CAN CALL
--------------------
Available Tools:
{self.available_tools}

Tool Metadata:
{self.toolbox_metadata}

--------------------
WHAT YOU MUST DO
--------------------
1) Understand what the target table represents from schema + examples.
2) Compare target schema vs source schema:
   - Identify which target columns can be directly projected/renamed
   - Identify which target columns require aggregation, reshaping, or combining tables
3) Decide the NEXT ACTION needed:
   - If the next required step is to decide WHICH operator comes next, use Add_Operator_Tool.
   - If the next required step is to CONFIGURE the most recently added operator (because it has no config yet),
     use the corresponding Configure_* tool.
   - If the target can be obtained from the current pipeline state with only projection/rename/filter,
     choose NO_MORE_OPERATOR.
4) Avoid repeating an operator type + config already in Operation History unless absolutely necessary.

--------------------
DECISION RULES
--------------------
Choose ADD_OPERATOR if any of these is true:
- target needs aggregation (e.g., target has fewer rows / summarizes source) -> GROUP_BY/AGGREGATE
- target needs combining multiple sources -> JOIN or UNION
- target is wide-to-long or long-to-wide -> PIVOT or UNPIVOT

Choose NO_MORE_OPERATOR if:
- the pipeline already yields target schema and semantics, and only trivial formatting remains
- OR adding any operator would be speculative / not supported by evidence from examples

--------------------
HOW TO MAP DECISION TO TOOL
--------------------
You MUST select exactly ONE tool_name from the available tools list.

A) If the most recent operator in Operation History is NOT FULLY CONFIGURED:
   - If the most recent operator is JOIN:
       tool_name = "Configure_Join_Operator_Tool"
       sub_goal must ask: "what tables should be joined and at which columns?"
   - If the most recent operator is GROUP_BY/AGGREGATE:
       tool_name = "Configure_GroupBy_Aggregate_Operator_Tool"
       sub_goal must ask: "which columns should be used for group by, which columns aggregated, and which functions?"
   - If the most recent operator is UNION:
       tool_name = "Configure_Union_Operator_Tool"
       sub_goal must ask: "what tables should be union-ed?"
   - If the most recent operator is PIVOT or UNPIVOT and there is no configure tool available:
       you must include a DRAFT config skeleton directly in sub_goal (and do NOT select a missing tool).

B) If there is no pending configuration (i.e., the latest operator is already configured, or there is no operator yet):
   - If decision = ADD_OPERATOR:
       tool_name = "Add_Operator_Tool"
       sub_goal must include:
         - decision: ADD_OPERATOR
         - operator_type (one of allowed operator types)
         - which input table(s) it applies to (source or intermediate)
         - what mismatch it resolves (very explicit)
         - a DRAFT config skeleton (keys/fields to be filled in by Configure tool when applicable)
   - If decision = NO_MORE_OPERATOR:
       tool_name = "NO_MORE_OPERATOR_Tool"
       sub_goal must say why no more operators are needed.

IMPORTANT: Put ALL details needed by the chosen tool into "context".
- Include target schema, source schema, relevant sample rows, and operation history.
- If referencing a file, include its exact path.
- If referencing columns, spell them exactly as in schema.
- If intermediate tables exist, include their names and schemas (from operation history / memory).

--------------------
OUTPUT REQUIREMENTS
--------------------
Return ONLY valid JSON for NextStep with keys: context, sub_goal, tool_name.
No extra keys. No prose outside JSON.

                        """
        else:
            query_prompt = f"""
Task: Analyze the given query to determine necessary skills and tools.

Inputs:
- Query: {question}
- Available tools: {self.available_tools}
- Metadata for tools: {self.toolbox_metadata}

Instructions:
1. Identify the main objectives in the query.
2. List the necessary skills and tools.
3. For each skill and tool, explain how it helps address the query.
4. Note any additional considerations.

Format your response with a summary of the query, lists of skills and tools with explanations, and a section for additional considerations.

Be biref and precise with insight. 
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
        prompt_logger.debug("="*80)
        prompt_logger.debug("ANALYZE_QUERY PROMPT:")
        prompt_logger.debug("="*80)
        prompt_logger.debug(query_prompt)
        prompt_logger.debug("="*80)

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
        if self.is_multimodal:
            prompt_generate_next_step = f"""
Task: Determine the optimal next step to address the given query based on the provided analysis, available tools, and previous steps taken.

Context:
Query: {question}
Image: {image}
Query Analysis: {query_analysis}

Available Tools:
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
- Capabilities of available tools
- Logical progression of problem-solving
- Outcomes from previous steps
- Current step count and remaining steps

3. Select ONE tool best suited for the next step, keeping in mind the limited number of remaining steps.

4. Formulate a specific, achievable sub-goal for the selected tool that maximizes progress towards answering the query.

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
- Select only ONE tool for this step.
- The sub-goal MUST directly address the query and be achievable by the selected tool.
- The Context section MUST include ALL necessary information for the tool to function, including ALL relevant file paths, data, and variables from previous steps.
- The tool name MUST exactly match one from the available tools list: {self.available_tools}.
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
            prompt_generate_next_step = f"""
Task: Determine the optimal next step to address the query using available tools and previous steps.

Context:
- **Query:** {question}
- **Query Analysis:** {query_analysis}
- **Available Tools:** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Previous Steps:** {memory.get_actions()}

Instructions:
1. Analyze the query, previous steps, and available tools.
2. Select the **single best tool** for the next step.
3. Formulate a specific, achievable **sub-goal** for that tool.
4. Provide all necessary **context** (data, file names, variables) for the tool to function.

Response Format:
1.  **Justification:** Explain your choice of tool and sub-goal.
2.  **Context:** Provide all necessary information for the tool.
3.  **Sub-Goal:** State the specific objective for the tool.
4.  **Tool Name:** State the exact name of the selected tool.

Rules:
- Select only ONE tool.
- The sub-goal must be directly achievable by the selected tool.
- The Context section must contain all information the tool needs to function.
- The response must end with the Context, Sub-Goal, and Tool Name sections in that order, with no extra content.
                    """

        # Log the full prompt
        prompt_logger.debug("="*80)
        prompt_logger.debug(f"GENERATE_NEXT_STEP PROMPT (Step {step_count}):")
        prompt_logger.debug("="*80)
        prompt_logger.debug(prompt_generate_next_step)
        prompt_logger.debug("="*80)

        next_step = self.llm_engine(prompt_generate_next_step, response_format=NextStep)
        if json_data is not None:
            json_data[f"action_predictor_{step_count}_prompt"] = (
                prompt_generate_next_step
            )
            json_data[f"action_predictor_{step_count}_response"] = str(next_step)
        return next_step

    def generate_final_output(self, question: str, image: str, memory: Memory) -> str:
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
        prompt_logger.debug("="*80)
        prompt_logger.debug("GENERATE_FINAL_OUTPUT PROMPT:")
        prompt_logger.debug("="*80)
        prompt_logger.debug(prompt_generate_final_output)
        prompt_logger.debug("="*80)

        # final_output = self.llm_engine_mm(input_data)
        # final_output = self.llm_engine(input_data)
        final_output = self.llm_engine_fixed(input_data)

        return final_output

    def generate_direct_output(self, question: str, image: str, memory: Memory) -> str:
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
        prompt_logger.debug("="*80)
        prompt_logger.debug("GENERATE_DIRECT_OUTPUT PROMPT:")
        prompt_logger.debug("="*80)
        prompt_logger.debug(prompt_generate_final_output)
        prompt_logger.debug("="*80)

        # final_output = self.llm_engine(input_data)
        final_output = self.llm_engine_fixed(input_data)
        # final_output = self.llm_engine_mm(input_data)

        return final_output
