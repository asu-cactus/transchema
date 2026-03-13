# agentflow/tools/add_unpivot/tool.py

import json
import re
from typing import Any, Dict, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Add_Unpivot_Tool"



def _extract_json_from_dollars(text: str) -> Optional[Dict]:
    """Extract JSON object from $...$ delimiters."""
    if not text:
        return None
    m = re.search(r"\$(.*?)\$", text, flags=re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1).strip())
    except Exception:
        return None


def get_unpivot_prompt(transformation_case_info: str) -> str:
    """Generate unpivot (melt) configuration prompt using transformation case information."""
    prompt = f"""
You are configuring an UNPIVOT (melt) operation for a data pipeline that transforms multiple source tables into a target table.

An UNPIVOT operation takes a wide table with multiple value columns and stacks those columns into rows, producing a narrower table with a key column (holding former column names) and a value column (holding the values).

{transformation_case_info}

Based on the source and target schema information above, determine the correct UNPIVOT configuration.

Instructions:
- Identify "id_vars": columns to keep as-is (row identifiers that should NOT be melted). These are columns that appear unchanged in the target.
- Identify "value_vars": columns whose values should be stacked into rows (the columns being melted). Leave empty list [] to melt all non-id_vars columns.
- Identify "var_name": the name for the new column that will hold the former column names (headers of the melted columns).
- Identify "value_name": the name for the new column that will hold the values from the melted columns.

You may reference intermediate results from the operation history as the input table.

Return ONLY the JSON unpivot specification enclosed in $ signs, in this exact format:
${"id_vars": ["col1", "col2"], "value_vars": ["col3", "col4"], "var_name": "key_column_name", "value_name": "value_column_name"}$

Where:
- "id_vars": list of columns to keep as row identifiers
- "value_vars": list of columns to melt into rows (use [] to melt all non-id columns)
- "var_name": name for the new column containing former column headers
- "value_name": name for the new column containing the cell values
    """
    return prompt


class Add_Unpivot_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description=(
                "A tool that configures an UNPIVOT (melt) operator by determining which columns "
                "to keep as row identifiers, which columns to stack into rows, and what to name "
                "the resulting key and value columns. Use when the target table is narrower than "
                "the source (i.e., multiple source columns should become rows in the output)."
            ),
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table Name, Target Schema, Target Examples, Source Information, and Operation History.",
            },
            output_type="dict - Contains 'unpivot_spec' (dict with id_vars, value_vars, var_name, value_name) and 'raw_response'.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n2. Target Schema: ...\\n3. Target Examples: ...\\n4. Source Information: ...\\n5. Operation History: [JOIN(...)]")',
                    "description": "Configure an UNPIVOT (melt) operation from transformation case information.",
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
        """Execute the unpivot configuration tool."""
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information"
            )

        full_prompt = get_unpivot_prompt(query)
        response = self.llm_engine(full_prompt)
        response_str = str(response)

        unpivot_spec = _extract_json_from_dollars(response_str)

        return {
            "unpivot_spec": unpivot_spec if unpivot_spec is not None else response_str.strip(),
            "raw_response": response_str,
        }


if __name__ == "__main__":
    tool = Add_Unpivot_Tool(model_string="gpt-4o-mini")
    print(
        tool.execute(
            query="""
1. Target Table Name: Target1_0
2. Target Schema: ['Country': string, 'Month': string, 'Value': float]
3. Target Examples: Country Month Value
   USA Jan 10.5
   USA Feb 12.3
4. Source Information:
   Source 0 Name: Source1_0_0
   Source 0 Schema: ['Country', 'Jan', 'Feb', 'Mar']
   Source 0 File Location: autopipeline-benchmarks/github-pipelines/length1_0/test_0.csv
5. Operation History: []
""".strip()
        )
    )
