# agentflow/tools/critique_pipeline/tool.py

from typing import Any, Dict

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


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

Hint 1:
Some column names (e.g., purpose, funded_year) may not match the values in the column (e.g., 5, 16844). In this case consider the column to be an aggregation target (e.g., count per purpose, sum for funded_year). They should not be used in Group By columns.

Hint 2:
If the pipeline produces more rows than expected: (1) A Group By/Aggregate may be missing. (2) An existing Group By may have too many attributes. (3) OUTER join should be replaced by INNER join. (4) Remove rows with NaN values.

Hint 3:
If the pipeline produces fewer rows than expected: (1) INNER join should be replaced by OUTER join. (2) Keep rows with NaN values. (3) Group By should be removed or use more Group By attributes.

Hint 4:
If multiple source tables share the same schema and the target also has the same schema, UNION must be used. However if m source tables share the same schema of k non-key columns, but the target has k x m non-key columns (renamed), JOIN should be applied on the primary key.

Hint 5:
Group By columns are never float types. They correspond to UNIQUE, non-float columns usually at the leftmost part of the target schema.

Hint 6:
If target examples contain duplicate keys or duplicate rows, Group By should NOT be used.

Hint 7:
If a column's average in target is significantly bigger than in sources, sum aggregation should be applied and this column excluded from Group By.

Hint 8:
JOIN is usually applied to two tables sharing the same primary key, or where one table has a foreign key referencing the other's primary key.

Hint 9:
Two tables may join on columns with different names but similar values (e.g., Code vs Country both containing country codes).

Hint 10:
All source tables must be used. If some share schemas, union them first, then join with the rest.

Hint 11:
NEVER use all target columns as GROUP BY columns.

Hint 12:
If target columns have constant numerical values per tuple, it may indicate a count aggregation after grouping.

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
