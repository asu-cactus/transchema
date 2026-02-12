# agentflow/tools/modify_pipeline/tool.py

from typing import Any, Dict

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Modify_Pipeline_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It modifies the pipeline based on the provided critique and sub-goal only — it does not execute transformations.
2) It requires a valid pipeline_id referencing a previously created pipeline in memory.
3) If the original pipeline or its critique are unclear, modifications may be suboptimal.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide the pipeline_id of the pipeline to modify.
2) Include the full transformation case info, the current pipeline definition, and its critique in the query.
3) The planner's sub-goal should clearly describe what modification is needed.
"""


def get_modify_pipeline_prompt(
    transformation_case_info: str,
    current_pipeline: str,
    critique: str,
    modification_goal: str,
) -> str:
    """Generate the prompt for modifying an existing pipeline."""
    prompt = f"""
You are modifying an existing data-transformation pipeline based on a critique and a specific modification goal.

{transformation_case_info}

Current Pipeline:
{current_pipeline}

Critique of Current Pipeline:
{critique}

Modification Goal:
{modification_goal}

Based on the critique and the modification goal, revise the pipeline. Provide the complete updated sequence of operations.

For each operation, provide:
- Operation type: JOIN, UNION, GROUP_BY/AGGREGATE, PIVOT, UNPIVOT
- Configuration: which tables/columns are involved and how

Guidelines:
- Address ALL issues identified in the critique.
- Follow the modification goal's direction.
- If multiple source tables share the same schema and the target also has the same schema, use UNION.
- If m source tables share the same schema of k non-key columns but the target has k x m renamed non-key columns, use JOIN on the primary key.
- Two tables may join on columns with different names but similar values.
- GROUP_BY columns must be non-float, unique-valued columns typically at the leftmost part of the target schema.
- If target examples contain duplicate keys or duplicate rows, GROUP_BY should NOT be used.
- All source tables must be used.

Format your response as:
$PIPELINE:
Step 1: <OPERATION_TYPE> - <configuration details>
Step 2: <OPERATION_TYPE> - <configuration details>
...
$
"""
    return prompt


def get_pipeline_critique_prompt(transformation_case_info: str, pipeline_plan: str) -> str:
    """Generate the prompt for critiquing the modified pipeline."""
    prompt = f"""
You are reviewing a modified data-transformation pipeline. Evaluate whether the pipeline will correctly produce the target table from the source tables.

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


class Modify_Pipeline_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that modifies an existing data transformation pipeline based on its critique and the planner's modification goal. Takes a pipeline_id to identify which pipeline to modify, applies changes, and produces an updated pipeline with a new critique.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table, Source Information, current pipeline definition, and its critique.",
                "pipeline_id": "str - The ID of the pipeline to modify (from a previous Create_Pipeline_Tool result).",
                "current_pipeline": "str - The current pipeline definition to modify.",
                "critique": "str - The critique of the current pipeline identifying issues.",
                "modification_goal": "str - Description of what modification should be made.",
            },
            output_type="dict - Contains pipeline_id, modified pipeline definition, new critique, and raw LLM responses.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n...", pipeline_id="pipeline_abc123", current_pipeline="Step 1: JOIN ...", critique="Assessment: PARTIALLY_CORRECT ...", modification_goal="Replace UNION with JOIN for tables with different schemas")',
                    "description": "Modify an existing pipeline based on its critique.",
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

    def execute(
        self,
        query: str = "",
        pipeline_id: str = "",
        current_pipeline: str = "",
        critique: str = "",
        modification_goal: str = "",
    ) -> Dict[str, Any]:
        """Modify an existing pipeline based on its critique and the modification goal."""
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information"
            )
        if not pipeline_id:
            raise ValueError(
                "pipeline_id parameter is required to identify which pipeline to modify"
            )

        # Step 1: Modify the pipeline
        modify_prompt = get_modify_pipeline_prompt(
            transformation_case_info=query,
            current_pipeline=current_pipeline,
            critique=critique,
            modification_goal=modification_goal,
        )
        modify_response = self.llm_engine(modify_prompt)
        modified_pipeline = str(modify_response)

        # Step 2: Critique the modified pipeline
        critique_prompt = get_pipeline_critique_prompt(query, modified_pipeline)
        critique_response = self.llm_engine(critique_prompt)
        new_critique = str(critique_response)

        return {
            "pipeline_id": pipeline_id,
            "pipeline": modified_pipeline,
            "critique": new_critique,
            "modify_prompt": modify_prompt,
            "critique_prompt": critique_prompt,
        }


if __name__ == "__main__":
    tool = Modify_Pipeline_Tool(model_string="gpt-4o-mini")
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
""".strip(),
            pipeline_id="pipeline_abc12345",
            current_pipeline="Step 1: UNION(Source4_31_0, Source4_31_1, Source4_31_2, Source4_31_3, Source4_31_4)",
            critique="Assessment: INCORRECT\nIssues: Source tables have different schemas so UNION is invalid. Should use JOIN on County column.\nSuggestions: JOIN all source tables on County.",
            modification_goal="Replace UNION with sequential JOINs on County column since source tables have different schemas.",
        )
    )
