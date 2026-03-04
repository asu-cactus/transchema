# agentflow/tools/critique_pipeline/tool.py

import sys
from pathlib import Path
from typing import Any, Dict

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool

_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[5])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)
from hints.hints_static import get_hints_section, CRITIQUE_HINT_IDS


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Critique_Pipeline_Tool"



def get_critique_prompt(transformation_case_info: str) -> str:
    """Generate the critique prompt using the provided transformation case information."""
    prompt = f"""
You are critiquing a data-pipeline that transforms multiple source tables to follow the schema of the target table. An LLM agent has been building this pipeline step by step. Review the current pipeline and suggest corrections.

Your task is to review the current operation history and suggest what operators need to be changed, added, or removed to correctly produce the target table.

{transformation_case_info}

For each operator you suggest, provide clear configuration:
--For Join, give the names of tables to be joined and the join attributes.
--For Union, give the names of tables to be unioned.
--For GroupBy, give the Group By attributes. Group by a couple of LEFTMOST column(s) of the target table schema. These columns must be string or integer types (NOT float) and contain unique values in the target examples.
--For Aggregate, give the aggregation function and aggregation column. Aggregation columns must not be included in group by columns.

Please pay attention to the following hints and apply relevant ones:

{get_hints_section(CRITIQUE_HINT_IDS, fmt="numbered")}

Based on your analysis, provide:
1. What is wrong with the current pipeline (if anything).
2. What specific operators and configurations should be added, changed, or removed.
3. The corrected sequence of operations.

Format your response as:
$CRITIQUE: <your detailed critique and corrected pipeline>$
    """
    return prompt


class Critique_Pipeline_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that critiques the current transformation pipeline and suggests corrections when the pipeline is close to completion but needs adjustments.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table, Source Information, and Operation History.",
            },
            output_type="dict - Contains the critique analysis with suggested corrections, plus raw LLM response and prompt.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n2. Target Schema: ...\\n3. Target Examples: ...\\n4. Source Information: ...\\n5. Operation History: [JOIN(...)]")',
                    "description": "Critique a pipeline that is close to completion.",
                }
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

    def execute(self, query: str = "") -> Dict[str, Any]:
        """Execute the critique tool with the provided transformation case information."""
        if not query:
            raise ValueError("query parameter is required and must contain transformation case information")

        full_prompt = get_critique_prompt(query)

        response = self.llm_engine(full_prompt)
        response_str = str(response)

        return {
            "critique": response_str,
            "raw_response": response_str,
            "prompt": full_prompt,
        }


if __name__ == "__main__":
    tool = Critique_Pipeline_Tool(model_string="gpt-4o-mini")
    print(
        tool.execute(
            query="""
1. Target Table Name: Target4_31
2. Target Schema: ['County': string, 'm1401': string, 'm1402': string, 'm1403': string, 'm1404': string]
3. Target Examples: County m1401 m1402 m1403 m1404
   El Paso $4,923,633 $5,116,438 $5,929,766 $5,535,184
4. Source Information:
   Source 0: Source4_31_0 Schema: ['County', 'm1403']
   Source 1: Source4_31_1 Schema: ['County']
   Source 2: Source4_31_2 Schema: ['County', 'm1401']
   Source 3: Source4_31_3 Schema: ['County', 'm1402']
   Source 4: Source4_31_4 Schema: ['County', 'm1404']
5. Operation History: [JOIN(Source4_31_0, Source4_31_1, on=County)]
""".strip()
        )
    )
