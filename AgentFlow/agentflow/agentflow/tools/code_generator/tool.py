# agentflow/tools/code_generator/tool.py

import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool

_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[5])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)
from hints.hints_static import get_hints_section, PYTHON_SCRIPT_HINT_IDS


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Code_Generator_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It generates Python transformation code but does not execute it.
2) Generated code quality depends on the completeness and clarity of source/target information provided.
3) Complex multi-step transformations with many source tables may require iterative refinement.
4) It relies on the memory (action history) to understand prior pipeline steps; incomplete memory may lead to suboptimal code.
5) The generated code assumes pandas is available in the execution environment.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide the full query containing Target Table Name, Target Schema, Target Examples, and Source Information with file locations.
2) Ensure memory contains the complete action history so the tool can follow the correct sequence of operations.
3) Include any error messages from previous code generation attempts so the tool can correct mistakes.
4) Specify the CSV save path where the result should be written.
"""


def _extract_python_code(response: str) -> Optional[str]:
    """Extract Python code block from LLM response."""
    if not response:
        return None
    match = re.search(r"```[Pp]ython\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def get_code_generation_prompt(query: str, memory_actions: str, error_string: str) -> str:
    """Build the code generation prompt using the query (case info), memory actions, and error history."""
    prompt = f"""You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in the action history below. The code should be immediately executable in a correct way, which means it should NOT contain any placeholder for brevity. For example, even if there exist hundreds of source tables, these data need to be loaded completely one by one or in a programmable way.

    Transformation Context:

    {query}

    Action History (follow this sequence of operations strictly):
    {memory_actions}

    Based on the transformation context and action history, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omitting any single statement. For example, please list all the source paths that will be used.

    Please quote the Python script between one single "```Python" and "```".

    Hints to be considered for Python code generation:
{get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt="bullet")}

 Please quote the Python script between one single "```Python" and "```".

 Errors in previous attempts: {error_string}
"""
    return prompt


class Code_Generator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description=(
                "A tool that generates executable Python transformation code based on the "
                "transformation query (target/source table information) and the action history "
                "from memory. It produces a complete pandas-based Python script that converts "
                "source tables into the target table format. The tool generates code only and "
                "does not execute it."
            ),
            tool_version="1.0.0",
            input_types={
                "query": "str - The full transformation context including Target Table Name, Target Schema, Target Examples, Source Information with file locations, and CSV save path.",
                "memory_actions": "str - (Optional) The action history from memory describing prior pipeline operations. Defaults to empty.",
                "error_string": "str - (Optional) Error messages from previous code generation attempts for iterative correction. Defaults to empty.",
            },
            output_type="dict - A dictionary containing the generated Python code, the raw LLM response, and the prompt used.",
            demo_commands=[
                {
                    "command": (
                        'execution = tool.execute(query="1. Target Table Name: Target1_0\\n'
                        '2. Target Schema: [\'State\': string, \'AverageTemperature\': float]\\n'
                        '3. Target Examples: ...\\n4. Source Information: ...\\n'
                        '5. Write the result to this path output.csv")'
                    ),
                    "description": "Generate Python transformation code from transformation case information.",
                },
                {
                    "command": (
                        'execution = tool.execute('
                        'query="1. Target Table Name: Target4_31\\n...", '
                        'memory_actions="Action Step 1: {\'tool_name\': \'Configure_Join_Operator_Tool\', ...}", '
                        'error_string="KeyError: \'County\'"'
                        ')'
                    ),
                    "description": "Generate code with action history and error correction context.",
                },
            ],
            user_metadata={"limitations": LIMITATION, "best_practices": BEST_PRACTICE},
        )

        print(f"Initializing Code_Generator_Tool with model_string: {model_string}")

        # NOTE: deterministic mode
        self.llm_engine = create_llm_engine(
            model_string=model_string,
            is_multimodal=False,
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

    def execute(self, query: str = "", memory_actions: str = "", error_string: str = "") -> Dict[str, Any]:
        """
        Generate Python transformation code based on the query and action history.

        Parameters:
            query (str): The full transformation context (target table info, source info, save path).
            memory_actions (str): The action history from memory describing prior operations.
            error_string (str): Error messages from previous attempts for iterative correction.

        Returns:
            dict: A dictionary containing:
                - 'generated_code': The extracted Python code (or None if extraction failed)
                - 'raw_response': The full LLM response
                - 'prompt': The prompt that was sent to the LLM
        """
        if not self.llm_engine:
            raise ValueError(
                "LLM engine not initialized. Please provide a valid model_string when initializing the tool."
            )

        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information."
            )

        # Build the code generation prompt
        full_prompt = get_code_generation_prompt(
            query=query,
            memory_actions=memory_actions if memory_actions else "No prior actions.",
            error_string=error_string if error_string else "No previous errors.",
        )

        # Call the LLM engine
        response = self.llm_engine(full_prompt)
        response_str = str(response)

        # Extract Python code from the response
        generated_code = _extract_python_code(response_str)

        return {
            "generated_code": generated_code,
            "raw_response": response_str,
            "prompt": full_prompt,
        }

    def get_metadata(self):
        """Returns the metadata for the Code_Generator_Tool."""
        metadata = super().get_metadata()
        metadata["require_llm_engine"] = self.require_llm_engine
        return metadata


if __name__ == "__main__":
    # Test command:
    """
    Run the following commands in the terminal to test the script:

    cd agentflow/tools/code_generator
    python tool.py
    """

    tool = Code_Generator_Tool(model_string="gpt-4o")

    # Get tool metadata
    metadata = tool.get_metadata()
    print("Tool Metadata:", metadata)

    # Sample query
    sample_query = """1. Target Table Name: Target4_31
2. Target Schema: ['County': string, 'm1401': string, 'm1402': string, 'm1403': string, 'm1404': string]
3. Target Examples: There are 17 available target examples:          County       m1401       m1402       m1403       m1404
10      El Paso  $4,923,633  $5,116,438  $5,929,766  $5,535,184
4. Source Information:
    Source 0 Name: Source4_31_0
    Source 0 Schema: ['County', 'm1403']
    Source 0 File Location: autopipeline-benchmarks/github-pipelines/length4_31/test_0.csv
    Source 1 Name: Source4_31_1
    Source 1 Schema: ['County']
    Source 1 File Location: autopipeline-benchmarks/github-pipelines/length4_31/test_1.csv
5. Write the result to this path output.csv"""

    sample_memory = """Action Step 1: {'tool_name': 'Configure_Join_Operator_Tool', 'sub_goal': 'Configure join between source tables', 'command': 'tool.execute(query=...)', 'result': {'join_spec': [['test_0.csv', 'test_2.csv'], ['test_0.County', 'test_2.County']]}}"""

    print("\n### Testing Code Generation ###")
    try:
        execution = tool.execute(
            query=sample_query,
            memory_actions=sample_memory,
            error_string="",
        )
        print("\n### Generated Code:")
        print(execution["generated_code"])
    except ValueError as e:
        print(f"Execution failed: {e}")

    print("\nDone!")
