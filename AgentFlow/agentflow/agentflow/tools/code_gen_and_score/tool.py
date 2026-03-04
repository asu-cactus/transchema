# agentflow/tools/code_gen_and_score/tool.py
#
# Operator-mode code generation tool. Uses its own prompt with updated hints.
# When invoked, solver.py detects this tool name and automatically executes the
# generated code + calculates the score, then merges the score into the memory entry.

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
TOOL_NAME = "Code_Gen_And_Score_Tool"


def _extract_python_code(response: str) -> Optional[str]:
    """Extract Python code block from LLM response."""
    if not response:
        return None
    match = re.search(r"```[Pp]ython\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def get_operator_code_generation_prompt(query: str, memory_actions: str, error_string: str) -> str:
    """Build the code generation prompt for operator-driven pipelines."""
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


class Code_Gen_And_Score_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description=(
                "A tool that generates executable Python transformation code from all operator "
                "configurations accumulated in memory, then automatically executes the code and "
                "calculates a score against the target table. Use this tool when:\n"
                "  1) The pipeline feels complete — to finalize and verify the result.\n"
                "  2) You need to materialize intermediate state to understand the current data "
                "shape before deciding which operator to add next.\n"
                "The score_summary in the result details what is correct and what still needs "
                "fixing (missed functional dependencies, keys, or target columns)."
            ),
            tool_version="1.0.0",
            input_types={
                "query": "str - The full transformation context including Target Table Name, Target Schema, Target Examples, Source Information with file locations, and CSV save path.",
                "memory_actions": "str - (Optional) The action history from memory describing prior operator configurations. Defaults to empty.",
                "error_string": "str - (Optional) Error messages from previous code generation attempts for iterative correction. Defaults to empty.",
            },
            output_type=(
                "dict - Contains 'generated_code' (Python script), 'raw_response' (full LLM output), "
                "and after solver execution: 'execution_success', 'score', 'score_fd', "
                "'column_mapping_score', 'score_summary', 'execution_error'."
            ),
            demo_commands=[
                {
                    "command": (
                        'execution = tool.execute(query="1. Target Table Name: Target1_0\\n'
                        '2. Target Schema: ...\\n3. Target Examples: ...\\n'
                        '4. Source Information: ...\\n5. Write the result to output.csv", '
                        'memory_actions="Action Step 1: {\'tool_name\': \'Configure_Join_Operator_Tool\', ...}")'
                    ),
                    "description": "Generate and score transformation code after operators are configured.",
                },
            ],
        )

        self.llm_engine = create_llm_engine(
            model_string=model_string,
            is_multimodal=False,
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

    def execute(
        self, query: str = "", memory_actions: str = "", error_string: str = ""
    ) -> Dict[str, Any]:
        """
        Generate Python transformation code based on query and operator action history.

        Parameters:
            query (str): Full transformation context (target info, source info, save path).
            memory_actions (str): Operator action history from memory.
            error_string (str): Prior error messages for iterative correction.

        Returns:
            dict: Contains 'generated_code' and 'raw_response'.
                  After solver.py execution: also contains score fields merged in.
        """
        if not self.llm_engine:
            raise ValueError(
                "LLM engine not initialized. Please provide a valid model_string."
            )
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information."
            )

        full_prompt = get_operator_code_generation_prompt(
            query=query,
            memory_actions=memory_actions if memory_actions else "No prior actions.",
            error_string=error_string if error_string else "No previous errors.",
        )

        response = self.llm_engine(full_prompt)
        response_str = str(response)
        generated_code = _extract_python_code(response_str)

        return {
            "generated_code": generated_code,
            "raw_response": response_str,
        }
