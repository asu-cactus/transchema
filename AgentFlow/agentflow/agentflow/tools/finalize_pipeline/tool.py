# agentflow/tools/finalize_pipeline/tool.py

from typing import Any, Dict

from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Finalize_Pipeline_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It does not execute or validate the pipeline; it only marks it as the selected final pipeline.
2) It requires a valid pipeline_id that exists in memory from a prior Create or Modify step.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Only finalize a pipeline after the verifier has confirmed the pipeline is complete and correct.
2) Provide the pipeline_id and the pipeline definition so the generator knows exactly which pipeline to materialize.
"""


class Finalize_Pipeline_Tool(BaseTool):
    require_llm_engine = False

    def __init__(self, model_string: str = None):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that marks a specific pipeline as the finalized/completed pipeline. Called when the verifier confirms execution is complete. The generator uses the finalized pipeline to produce the final output.",
            tool_version="1.0.0",
            input_types={
                "pipeline_id": "str - The ID of the pipeline to mark as finalized.",
                "pipeline": "str - (Optional) The pipeline definition to include in the finalization record.",
            },
            output_type="dict - Contains the finalization signal, pipeline_id, and pipeline definition.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(pipeline_id="pipeline_a3f1b2c4", pipeline="Step 1: JOIN ...")',
                    "description": "Mark a pipeline as finalized for materialization.",
                }
            ],
            user_metadata={"limitations": LIMITATION, "best_practices": BEST_PRACTICE},
        )

    def execute(
        self, pipeline_id: str = "", pipeline: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Mark a pipeline as finalized."""
        if not pipeline_id:
            raise ValueError(
                "pipeline_id parameter is required to identify which pipeline to finalize"
            )

        return {
            "signal": "PIPELINE_FINALIZED",
            "pipeline_id": pipeline_id,
            "pipeline": pipeline,
            "message": f"Pipeline '{pipeline_id}' has been marked as the finalized pipeline for materialization.",
        }


if __name__ == "__main__":
    tool = Finalize_Pipeline_Tool()
    print(
        tool.execute(
            pipeline_id="pipeline_a3f1b2c4",
            pipeline="Step 1: JOIN(Source4_31_0, Source4_31_2, on=County)\nStep 2: JOIN(result, Source4_31_3, on=County)",
        )
    )
