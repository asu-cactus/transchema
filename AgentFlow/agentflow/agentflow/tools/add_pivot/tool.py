# agentflow/tools/add_pivot/tool.py

import json
import re
from typing import Any, Dict, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Add_Pivot_Tool"



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


def get_pivot_prompt(transformation_case_info: str) -> str:
    """Generate pivot configuration prompt using transformation case information."""
    prompt = f"""
You are configuring a PIVOT operation for a data pipeline that transforms multiple source tables into a target table.

A PIVOT operation takes rows and turns distinct values from one column into new column headers, aggregating values from another column.

{transformation_case_info}

Based on the source and target schema information above, determine the correct PIVOT configuration.

Instructions:
- Identify the "index" columns: columns kept as row identifiers (typically the leftmost unique columns in the target).
- Identify the "columns" field: the source column whose distinct values become new column headers in the target.
- Identify the "values" field: the source column whose values fill the pivoted cells.
- Identify the "aggfunc": the aggregation function to apply if multiple rows map to the same cell. Common choices: "first", "sum", "mean", "count". Use "first" if values are unique per cell.
- The result column names after pivot should match the target schema. Note this in your reasoning.

You may reference intermediate results from the operation history as the input table (e.g., join_result_0, union_result_0).

Return ONLY the JSON pivot specification enclosed in $ signs, in this exact format:
${"index": ["col1", "col2"], "columns": "pivot_key_col", "values": "value_col", "aggfunc": "first"}$

Where:
- "index": list of column names to keep as row identifiers
- "columns": the column whose values become new column names
- "values": the column whose values fill the pivoted cells
- "aggfunc": aggregation function ("first", "sum", "mean", "count")
    """
    return prompt


class Add_Pivot_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description=(
                "A tool that configures a PIVOT operator by determining which column's values "
                "become new column headers, which column provides the values, and which columns "
                "serve as row identifiers. Use when the target table is wider than the source "
                "(i.e., row values from one column should become separate columns in the output)."
            ),
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table Name, Target Schema, Target Examples, Source Information, and Operation History.",
            },
            output_type="dict - Contains 'pivot_spec' (dict with index, columns, values, aggfunc) and 'raw_response'.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n2. Target Schema: ...\\n3. Target Examples: ...\\n4. Source Information: ...\\n5. Operation History: [JOIN(...)]")',
                    "description": "Configure a PIVOT operation from transformation case information.",
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
        """Execute the pivot configuration tool."""
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information"
            )

        full_prompt = get_pivot_prompt(query)
        response = self.llm_engine(full_prompt)
        response_str = str(response)

        pivot_spec = _extract_json_from_dollars(response_str)

        return {
            "pivot_spec": pivot_spec if pivot_spec is not None else response_str.strip(),
            "raw_response": response_str,
        }


if __name__ == "__main__":
    tool = Add_Pivot_Tool(model_string="gpt-4o-mini")
    print(
        tool.execute(
            query="""
1. Target Table Name: Target1_0
2. Target Schema: ['Country': string, 'Jan': float, 'Feb': float, 'Mar': float]
3. Target Examples: Country Jan Feb Mar
   USA 10.5 12.3 11.1
4. Source Information:
   Source 0 Name: Source1_0_0
   Source 0 Schema: ['Country', 'Month', 'Value']
   Source 0 File Location: autopipeline-benchmarks/github-pipelines/length1_0/test_0.csv
5. Operation History: []
""".strip()
        )
    )
