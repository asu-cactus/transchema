import json
import os
import re
import logging
from typing import Any, Tuple

from PIL import Image

from agentflow.engine.factory import create_llm_engine
from agentflow.models.formatters import MemoryVerification, PipelineVerification
from agentflow.models.memory import Memory

# Get the prompt logger
prompt_logger = logging.getLogger("agentflow.prompts")


class Verifier:
    def __init__(
        self,
        llm_engine_name: str,
        llm_engine_fixed_name: str = "dashscope",
        toolbox_metadata: dict = None,
        available_tools: list = None,
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

    def get_image_info(self, image_path: str) -> dict:
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

    def verificate_context(
        self,
        question: str,
        image: str,
        query_analysis: str,
        memory: Memory,
        step_count: int = 0,
        json_data: Any = None,
    ) -> Any:
        image_info = self.get_image_info(image)
        if self.is_multimodal:
            prompt_memory_verification = f"""
Task: Thoroughly evaluate the completeness and accuracy of the memory for fulfilling the given query, considering the potential need for additional tool usage.

Context:
Query: {question}
Image: {image_info}
Available Tools: {self.available_tools}
Toolbox Metadata: {self.toolbox_metadata}
Initial Analysis: {query_analysis}
Memory (tools used and results): {memory.get_actions()}

Detailed Instructions:
1. Carefully analyze the query, initial analysis, and image (if provided):
   - Identify the main objectives of the query.
   - Note any specific requirements or constraints mentioned.
   - If an image is provided, consider its relevance and what information it contributes.

2. Review the available tools and their metadata:
   - Understand the capabilities and limitations and best practices of each tool.
   - Consider how each tool might be applicable to the query.

3. Examine the memory content in detail:
   - Review each tool used and its execution results.
   - Assess how well each tool's output contributes to answering the query.

4. Critical Evaluation (address each point explicitly):
   a) Completeness: Does the memory fully address all aspects of the query?
      - Identify any parts of the query that remain unanswered.
      - Consider if all relevant information has been extracted from the image (if applicable).

   b) Unused Tools: Are there any unused tools that could provide additional relevant information?
      - Specify which unused tools might be helpful and why.

   c) Inconsistencies: Are there any contradictions or conflicts in the information provided?
      - If yes, explain the inconsistencies and suggest how they might be resolved.

   d) Verification Needs: Is there any information that requires further verification due to tool limitations?
      - Identify specific pieces of information that need verification and explain why.

   e) Ambiguities: Are there any unclear or ambiguous results that could be clarified by using another tool?
      - Point out specific ambiguities and suggest which tools could help clarify them.

5. Final Determination:
   Based on your thorough analysis, decide if the memory is complete and accurate enough to generate the final output, or if additional tool usage is necessary.

Response Format:

If the memory is complete, accurate, AND verified:
Explanation:
<Provide a detailed explanation of why the memory is sufficient. Reference specific information from the memory and explain its relevance to each aspect of the task. Address how each main point of the query has been satisfied.>

Conclusion: STOP

If the memory is incomplete, insufficient, or requires further verification:
Explanation:
<Explain in detail why the memory is incomplete. Identify specific information gaps or unaddressed aspects of the query. Suggest which additional tools could be used, how they might contribute, and why their input is necessary for a comprehensive response.>

Conclusion: CONTINUE

IMPORTANT: Your response MUST end with either 'Conclusion: STOP' or 'Conclusion: CONTINUE' and nothing else. Ensure your explanation thoroughly justifies this conclusion.
"""
        else:
            # Operator mode: check whether generated code exists in memory and score is satisfactory
            if self.execute_pipeline:
                score_check_section = """
3. **Code and Score Check** — Look for results from `Code_Gen_And_Score_Tool` in memory:
   - If a `Code_Gen_And_Score_Tool` result is present AND `score = 1.0` AND `score_summary` shows no missed functional dependencies, no missed ground-truth keys, and no missed target columns → conclude **STOP**.
   - If a `Code_Gen_And_Score_Tool` result is present but `score < 1.0` OR there are missed items in any category → conclude **CONTINUE** (more operators or critique are needed).
   - If no `Code_Gen_And_Score_Tool` result is in memory yet → the pipeline has not been verified; conclude **CONTINUE**.
   - If `execution_success = False` in the last `Code_Gen_And_Score_Tool` result → code execution failed; conclude **CONTINUE**.
"""
            else:
                score_check_section = """
3. **Code Check** — Look for results from `Code_Gen_And_Score_Tool` in memory:
   - If generated code is present and the pipeline looks complete → conclude **STOP**.
   - Otherwise conclude **CONTINUE**.
"""

            prompt_memory_verification = f"""
Task: Evaluate whether the operator-driven transformation pipeline has produced a correct and complete result, or whether more steps are needed.

Context:
- **Query:** {question}
- **Available Tools:** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Initial Analysis:** {query_analysis}
- **Memory (Tools Used & Results):** {memory.get_actions()}

Instructions:
1. Review the query, the operator configurations in memory (Join, Union, GroupBy, Pivot, Unpivot), and any code generation results.
2. Identify whether all necessary operators have been configured to produce the target schema.
{score_check_section}
Final Determination:
- Conclude **STOP** only when `Code_Gen_And_Score_Tool` has been run AND the score is 1.0 with no missed items.
- Conclude **CONTINUE** in all other cases (operators still missing, code not yet generated, score < 1.0, or execution failed).

IMPORTANT: The response must end with either "Conclusion: STOP" or "Conclusion: CONTINUE".
"""

        input_data = [prompt_memory_verification]
        if image_info:
            try:
                with open(image_info["image_path"], "rb") as file:
                    image_bytes = file.read()
                input_data.append(image_bytes)
            except Exception as e:
                print(f"Error reading image file: {str(e)}")

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(f"VERIFICATE_CONTEXT PROMPT (Step {step_count}):")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_memory_verification)
        prompt_logger.debug("=" * 80)

        stop_verification = self.llm_engine_fixed(
            input_data, response_format=MemoryVerification
        )
        if json_data is not None:
            json_data[f"verifier_{step_count}_prompt"] = input_data
            json_data[f"verifier_{step_count}_response"] = str(stop_verification)
        return stop_verification

    def verificate_context_with_additional_info(
        self,
        question: str,
        query_analysis: str,
        memory: Memory,
        additional_context: str,
        step_count: int = 0,
        json_data: Any = None,
    ) -> Any:
        """
        Verify context with additional information (e.g., correct transformation pipeline, scores, etc.)
        This method is non-multimodal and focuses on data transformation tasks.

        Args:
            question: The user query
            query_analysis: Initial analysis of the query
            memory: Memory object containing action history
            additional_context: Additional context like correct pipeline or evaluation criteria
            step_count: Current step count
            json_data: Optional JSON data for logging

        Returns:
            Verification response indicating STOP or CONTINUE
        """
        prompt_memory_verification = f"""
Task: Evaluate if the current memory (action history) is complete and accurate enough to answer the query, considering the additional context provided.

Context:
- **Query:** {question}
- **Available Tools:** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Initial Analysis:** {query_analysis}
- **Memory (Tools Used & Results):** {memory.get_actions()}

Additional Context (Reference Information):
{additional_context}

Instructions:
1. Review the query, initial analysis, and memory (action history).
2. Compare the actions taken in memory with the verification information provided [if it is provided]:
   - Does the memory's approach align with the expected pattern or solution indicated in the verification information?
3. Assess the completeness of the memory:
   - Does it fully address all parts of the query?
   - Are all required transformations/operations present?
4. Check for potential issues:
   - Are there any inconsistencies between the memory and the additional context?
   - Is any information ambiguous or in need of verification?
   - Are there operations in the additional context that haven't been executed yet?
5. Determine if any unused tools could provide missing information or operations.

Final Determination:
- If the memory is sufficient and aligns with the additional context, explain why and conclude with "STOP".
- If more information or operations are needed, explain:
  * What's missing compared to the additional context
  * Which tools or operations should be used next
  * Why they are necessary
  Then conclude with "CONTINUE".

Response Format:
Explanation:
<Provide a detailed analysis explaining your decision. Reference both the memory and the additional context.>

Conclusion: [STOP or CONTINUE]

IMPORTANT: The response must end with either "Conclusion: STOP" or "Conclusion: CONTINUE".
"""

        input_data = [prompt_memory_verification]

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(
            f"VERIFICATE_CONTEXT_WITH_ADDITIONAL_INFO PROMPT (Step {step_count}):"
        )
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_memory_verification)
        prompt_logger.debug("=" * 80)

        stop_verification = self.llm_engine_fixed(
            input_data, response_format=MemoryVerification
        )
        if json_data is not None:
            json_data[f"verifier_with_context_{step_count}_prompt"] = input_data
            json_data[f"verifier_with_context_{step_count}_response"] = str(
                stop_verification
            )
        return stop_verification

    def verificate_context_pipeline(
        self,
        question: str,
        image: str,
        query_analysis: str,
        memory: Memory,
        step_count: int = 0,
        json_data: Any = None,
    ) -> Any:
        """Pipeline-level verification that also identifies which pipeline to finalize."""
        # Conditionally add score-based guidance when execute_pipeline is enabled
        if self.execute_pipeline:
            score_instruction = """
4. **Score Understanding**: The overall score (0.0 to 1.0, higher is better) compares the generated output table against the target table using three components. If a `score_summary` is present in any result in memory, interpret it as follows:

   - **Functional Dependency Matching** (`functional_dependency_f1_score`): A functional dependency is a data constraint where knowing one set of column values determines another column's value (e.g., city determines country). If this score is below 1.0 and `functional_dependencies.missed` is non-empty, the output is missing grouping constraints that the target has. The correct fix is to add a GROUP BY using the key columns of the target table with appropriate aggregations at the end of the pipeline.

   - **Key Matching** (`keys.missed_ground_truth_keys`): Keys are the minimal sets of columns that uniquely identify each row in the target. If `missed_ground_truth_keys` is non-empty, the output has duplicate rows or incorrect grouping. The correct fix is to add a GROUP BY on the columns listed in `missed_ground_truth_keys` with appropriate aggregations.

   - **Column Mapping** (`column_mapping_score` and `column_mappings.missed_target_columns`): Checks whether all target columns are present in the output. If `missed_target_columns` is non-empty, those columns are absent from the output. The correct fix is to add JOINs with the source tables that contain those missing columns.

   - **The pipeline is ONLY correct when ALL three components are satisfied**: overall_score = 1.0, no missed functional dependencies, no missed ground truth keys, and no missed target columns. If any of these items are present, the pipeline is incomplete and MUST be refined — do NOT stop.

5. Score thresholds:
   - overall_score = 1.0 AND `functional_dependencies.missed` is empty AND `keys.missed_ground_truth_keys` is empty AND `column_mappings.missed_target_columns` is empty → strong evidence the pipeline is correct → recommend STOP.
   - Any missed item or low score → pipeline needs changes → recommend CONTINUE.
   - Failed execution → pipeline has code errors → recommend CONTINUE.

6. If the pipeline is complete and correct, identify the **pipeline_id** of the finalized pipeline from the memory."""
        else:
            score_instruction = """
4. If the pipeline is complete, identify the **pipeline_id** of the finalized pipeline from the memory."""

        prompt_memory_verification = f"""
Task: Evaluate if the current pipeline is complete and correct enough to produce the target transformation, or if more modifications are needed.

Context:
- **Query:** {question}
- **Available Tools:** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Initial Analysis:** {query_analysis}
- **Memory (Tools Used & Results):** {memory.get_actions()}

Instructions:
1. Review the query and the pipeline(s) created/modified in memory.
2. Assess completeness: Does the latest pipeline fully address the target transformation?
3. Check the critique: If the latest pipeline's critique says CORRECT, the pipeline is likely ready. However, the critique alone is not sufficient — the score must also confirm correctness (see below).
{score_instruction}

Final Determination:
- If the pipeline is complete and correct (critique says CORRECT AND score confirms all three components are satisfied):
  * Explain why
  * Provide the pipeline_id to finalize (from the most recent Create_New_Pipeline or Refine_Existing_Pipeline result in memory)
  * Conclude with "STOP"
- If modifications are still needed (any score component has missed items, or execution failed, or no score yet):
  * Explain what's missing or incorrect
  * Conclude with "CONTINUE"

IMPORTANT: The response must end with either "Conclusion: STOP" or "Conclusion: CONTINUE".
If STOP, you MUST include the finalized_pipeline_id field with the pipeline_id to finalize.
"""

        input_data = [prompt_memory_verification]

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(f"VERIFICATE_CONTEXT_PIPELINE PROMPT (Step {step_count}):")
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_memory_verification)
        prompt_logger.debug("=" * 80)

        stop_verification = self.llm_engine_fixed(
            input_data, response_format=PipelineVerification
        )
        if json_data is not None:
            json_data[f"verifier_pipeline_{step_count}_prompt"] = input_data
            json_data[f"verifier_pipeline_{step_count}_response"] = str(
                stop_verification
            )
        return stop_verification

    def verificate_context_pipeline_with_additional_info(
        self,
        question: str,
        query_analysis: str,
        memory: Memory,
        additional_context: str,
        step_count: int = 0,
        json_data: Any = None,
    ) -> Any:
        """Pipeline-level verification with additional context that also identifies which pipeline to finalize."""
        # Conditionally add score-based guidance when execute_pipeline is enabled
        if self.execute_pipeline:
            score_instruction = """
5. **Score Understanding**: The overall score (0.0 to 1.0, higher is better) compares the generated output table against the target table using three components. If a `score_summary` is present in any result in memory, interpret it as follows:

   - **Functional Dependency Matching** (`functional_dependency_f1_score`): A functional dependency is a data constraint where knowing one set of column values determines another column's value (e.g., city determines country). If this score is below 1.0 and `functional_dependencies.missed` is non-empty, the output is missing grouping constraints that the target has. The correct fix is to add a GROUP BY using the key columns of the target table with appropriate aggregations at the end of the pipeline.

   - **Key Matching** (`keys.missed_ground_truth_keys`): Keys are the minimal sets of columns that uniquely identify each row in the target. If `missed_ground_truth_keys` is non-empty, the output has duplicate rows or incorrect grouping. The correct fix is to add a GROUP BY on the columns listed in `missed_ground_truth_keys` with appropriate aggregations.

   - **Column Mapping** (`column_mapping_score` and `column_mappings.missed_target_columns`): Checks whether all target columns are present in the output. If `missed_target_columns` is non-empty, those columns are absent from the output. The correct fix is to add JOINs with the source tables that contain those missing columns.

   - **The pipeline is ONLY correct when ALL three components are satisfied**: overall_score = 1.0, no missed functional dependencies, no missed ground truth keys, and no missed target columns. If any of these items are present, the pipeline is incomplete and MUST be refined — do NOT stop.

6. Score thresholds:
   - overall_score = 1.0 AND `functional_dependencies.missed` is empty AND `keys.missed_ground_truth_keys` is empty AND `column_mappings.missed_target_columns` is empty → strong evidence the pipeline is correct → recommend STOP.
   - Any missed item or low score → pipeline needs changes → recommend CONTINUE.
   - Failed execution → pipeline has code errors → recommend CONTINUE.

7. If the pipeline is complete and correct, identify the **pipeline_id** of the finalized pipeline from the memory."""
        else:
            score_instruction = """
5. If the pipeline is complete, identify the **pipeline_id** of the finalized pipeline from the memory."""

        prompt_memory_verification = f"""
Task: Evaluate if the current pipeline is complete and correct enough to produce the target transformation, considering the additional context provided.

Context:
- **Query:** {question}
- **Available Tools:** {self.available_tools}
- **Toolbox Metadata:** {self.toolbox_metadata}
- **Initial Analysis:** {query_analysis}
- **Memory (Tools Used & Results):** {memory.get_actions()}

Additional Context (Reference Information):
{additional_context}

Instructions:
1. Review the query and the pipeline(s) created/modified in memory.
2. Compare with the additional context — does the pipeline align with the expected approach?
3. Assess completeness: Does the latest pipeline fully address the target transformation?
4. Check the critique: If the latest pipeline's critique says CORRECT, the pipeline is likely ready. However, the critique alone is not sufficient — the score must also confirm correctness (see below).
{score_instruction}

Final Determination:
- If the pipeline is complete, correct, and aligns with the additional context (critique says CORRECT AND score confirms all three components are satisfied):
  * Explain why
  * Provide the pipeline_id to finalize (from the most recent Create_New_Pipeline or Refine_Existing_Pipeline result in memory)
  * Conclude with "STOP"
- If modifications are still needed (any score component has missed items, or execution failed, or no score yet):
  * Explain what's missing or incorrect
  * Conclude with "CONTINUE"

IMPORTANT: The response must end with either "Conclusion: STOP" or "Conclusion: CONTINUE".
If STOP, you MUST include the finalized_pipeline_id field with the pipeline_id to finalize.
"""

        input_data = [prompt_memory_verification]

        # Log the full prompt
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(
            f"VERIFICATE_CONTEXT_PIPELINE_WITH_ADDITIONAL_INFO PROMPT (Step {step_count}):"
        )
        prompt_logger.debug("=" * 80)
        prompt_logger.debug(prompt_memory_verification)
        prompt_logger.debug("=" * 80)

        stop_verification = self.llm_engine_fixed(
            input_data, response_format=PipelineVerification
        )
        if json_data is not None:
            json_data[f"verifier_pipeline_with_context_{step_count}_prompt"] = (
                input_data
            )
            json_data[f"verifier_pipeline_with_context_{step_count}_response"] = str(
                stop_verification
            )
        return stop_verification

    def extract_conclusion(self, response: Any) -> Tuple[str, str]:
        finalized_pipeline_id = None

        if isinstance(response, str):
            # Attempt to parse the response as JSON
            try:
                response_dict = json.loads(response)
                if self.granularity == "pipeline":
                    response = PipelineVerification(**response_dict)
                else:
                    response = MemoryVerification(**response_dict)
            except Exception as e:
                print(f"Failed to parse response as JSON: {str(e)}")

        if isinstance(response, PipelineVerification):
            analysis = response.analysis
            stop_signal = response.stop_signal
            finalized_pipeline_id = response.finalized_pipeline_id
            if stop_signal:
                return analysis, "STOP", finalized_pipeline_id
            else:
                return analysis, "CONTINUE", finalized_pipeline_id

        if isinstance(response, MemoryVerification):
            analysis = response.analysis
            stop_signal = response.stop_signal
            if stop_signal:
                return analysis, "STOP"
            else:
                return analysis, "CONTINUE"
        else:
            analysis = response
            pattern = r"conclusion\**:?\s*\**\s*(\w+)"
            matches = list(re.finditer(pattern, response, re.IGNORECASE | re.DOTALL))
            if matches:
                conclusion = matches[-1].group(1).upper()
                if conclusion in ["STOP", "CONTINUE"]:
                    return analysis, conclusion

            # If no valid conclusion found, search for STOP or CONTINUE anywhere in the text
            if "stop" in response.lower():
                return analysis, "STOP"
            elif "continue" in response.lower():
                return analysis, "CONTINUE"
            else:
                print(
                    "No valid conclusion (STOP or CONTINUE) found in the response. Continuing..."
                )
                return analysis, "CONTINUE"
