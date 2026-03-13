# agentflow/tools/configure_union_operator/tool.py

import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool

_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[5])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)


TOOL_NAME = "Configure_Union_Operator_Tool"



def get_union_prompt(transformation_case_info: str) -> str:
    """Generate union prompt using the provided transformation case information."""
    prompt = f"""
You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be Union-ed?". Take this decision based on "Operation History",few shot examples, "Source" and "Target" (table schema as well as the examples) information provided below.

{transformation_case_info}

- Please answer which tables should be unioned.
- Apply UNION to tables that have exactly the same schema without renaming columns.
- Choose tables having exactly the same schema to union.
- Try not to repeat operation and it's configuration. i.e. Union on tables should only appear once in "Operation History".
- You should only answer from available tables of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in format of list where elements are quoted by $. I.e. [$table1$, $table2$, ...].
    """
    return prompt


def _extract_tables_from_dollar_list(text: str) -> Optional[List[str]]:
    """Extract table names from the [$t1$, $t2$] style output."""
    if not text:
        return None

    # Capture all $...$ occurrences
    tables = [m.strip() for m in re.findall(r"\$([^$]+)\$", text)]
    if tables:
        return tables

    # Fallback: try to parse as a python list literal
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, list):
            return [str(x) for x in obj]
    except Exception:
        pass

    return None


class Configure_Union_Operator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that configures a UNION operator by selecting which tables should be unioned.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table Name, Target Schema, Target Examples, and Multi Source Information.",
            },
            output_type="dict - Contains the union table list plus raw LLM response and prompt.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n2. Target Schema: ...\\n3. Target Examples: ...\\n4. Multi Source Information: ...")',
                    "description": "Configure a UNION from transformation case information.",
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

    def execute(self, query: str = "", **kwargs) -> Dict[str, Any]:
        """Execute the tool with the provided transformation case information."""
        if not query:
            raise ValueError("query parameter is required and must contain transformation case information")

        full_prompt = get_union_prompt(query)

        response = self.llm_engine(full_prompt)
        response_str = str(response)

        tables = _extract_tables_from_dollar_list(response_str)

        return {
            "union_tables": tables,
            "raw_response": response_str,
            "prompt": full_prompt,
        }


if __name__ == "__main__":
    tool = Configure_Union_Operator_Tool(model_string="gpt-4o-mini")
    print(
        tool.execute(
            query="""
1. Target Table Name: Target1_0
2. Target Schema: ['State': string, 'AverageTemperature': float]
3. Target Examples: State AverageTemperature
Zhejiang 16.18
4. Multi Source Information:
Source 0 Name: Source1_0_0
Source 0 Schema: ['dt', 'AverageTemperature', 'AverageTemperatureUncertainty', 'State', 'Country']
5. Operation History: []
""".strip()
        )
    )
