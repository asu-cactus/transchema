# agentflow/tools/create_pipeline/tool.py

import uuid
from typing import Any, Dict

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Create_Pipeline_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It designs the pipeline based on schemas, examples, and source information only — it does not execute transformations.
2) The quality of the pipeline depends on how representative the provided target examples are.
3) It generates a pipeline plan and a critique in a single step; the critique may miss edge cases that only appear during execution.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide complete target and source schemas with representative examples.
2) Include all source table information so the tool can reason about the full pipeline.
3) Use this tool at the start to design the overall pipeline before configuring individual operators.
"""


def get_pipeline_design_prompt(transformation_case_info: str) -> str:
    """Generate the prompt for designing a full pipeline."""
    prompt = f"""
You are designing a complete data-transformation pipeline that transforms multiple source tables into a target table. Your job is to plan the FULL sequence of operations needed.

{transformation_case_info}

Based on the above information, design the complete pipeline by specifying the ordered sequence of operations needed.

For each operation, provide:
- Operation type: JOIN, UNION, GROUP_BY/AGGREGATE, PIVOT, UNPIVOT
- Configuration: which tables/columns are involved and how

Guidelines:
- If multiple source tables share the same schema and the target also has the same schema, use UNION.
- If m source tables share the same schema of k non-key columns but the target has k x m renamed non-key columns, use JOIN on the primary key.
- Two tables may join on columns with different names but similar values (e.g., Code vs Country both containing country codes).
- GROUP_BY columns must be non-float, unique-valued columns typically at the leftmost part of the target schema.
- If target examples contain duplicate keys or duplicate rows, GROUP_BY should NOT be used.
- All source tables must be used.
- If some source tables share schemas, union them first, then join with the rest.

Format your response as:
$PIPELINE:
Step 1: <OPERATION_TYPE> - <configuration details>
Step 2: <OPERATION_TYPE> - <configuration details>
...
$
"""
    return prompt


def get_pipeline_critique_prompt(transformation_case_info: str, pipeline_plan: str) -> str:
    """Generate the prompt for critiquing a designed pipeline."""
    prompt = f"""
You are reviewing a proposed data-transformation pipeline. Evaluate whether the pipeline will correctly produce the target table from the source tables.

{transformation_case_info}

Proposed Pipeline:
{pipeline_plan}

Review the pipeline and provide:
1. Whether the pipeline is correct, partially correct, or incorrect.
2. What specific issues exist (if any): missing operations, wrong order, wrong configurations.
3. Suggested corrections with specific operator configurations.

Hints to consider:
- If the pipeline would produce more rows than expected: a GROUP_BY/AGGREGATE may be missing, or OUTER join should be INNER join.
- If the pipeline would produce fewer rows than expected: INNER join should be OUTER join, or GROUP_BY should be removed.
- All source tables must be used.
- GROUP_BY columns are never float types.
- Two tables may join on columns with different names but similar values.

Format your response as:
$CRITIQUE:
Assessment: <CORRECT / PARTIALLY_CORRECT / INCORRECT>
Issues: <list of issues or "None">
Suggestions: <specific corrections or "None">
$
"""
    return prompt


class Create_Pipeline_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that designs a complete data transformation pipeline from scratch. It generates a full sequence of operations (JOIN, UNION, GROUP_BY/AGGREGATE, etc.) and critiques the plan. Returns a pipeline_id, the pipeline definition, and the critique.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table, Source Information, and any relevant context.",
            },
            output_type="dict - Contains pipeline_id, pipeline definition (sequence of operations), critique, and raw LLM responses.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n2. Target Schema: [State: string, AverageTemperature: float]\\n3. Target Examples: ...\\n4. Source Information: ...")',
                    "description": "Design a complete pipeline for a transformation case.",
                }
            ],
            user_metadata={"limitations": LIMITATION, "best_practices": BEST_PRACTICE},
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
        """Design a new pipeline and critique it."""
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information"
            )

        # Generate a unique pipeline ID
        pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"

        # Step 1: Design the pipeline
        design_prompt = get_pipeline_design_prompt(query)
        design_response = self.llm_engine(design_prompt)
        pipeline_plan = str(design_response)

        # Step 2: Critique the pipeline
        critique_prompt = get_pipeline_critique_prompt(query, pipeline_plan)
        critique_response = self.llm_engine(critique_prompt)
        critique = str(critique_response)

        return {
            "pipeline_id": pipeline_id,
            "pipeline": pipeline_plan,
            "critique": critique,
            "design_prompt": design_prompt,
            "critique_prompt": critique_prompt,
        }


if __name__ == "__main__":
    tool = Create_Pipeline_Tool(model_string="gpt-4o-mini")
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
""".strip()
        )
    )
