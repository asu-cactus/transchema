# agentflow/tools/start_again/tool.py

from typing import Any, Dict

from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Start_Again_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It does not undo any previous operations; it only adds a signal to memory.
2) Subsequent tools must respect the START_AGAIN marker and ignore prior operations.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Use this tool when the pipeline has gone significantly wrong and needs a fresh start.
2) The planner should only invoke this when prior operations are fundamentally incorrect, not for minor adjustments (use Critique_Pipeline_Tool for those).
"""


class Start_Again_Tool(BaseTool):
    require_llm_engine = False

    def __init__(self, model_string: str = None):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that signals the pipeline should be restarted. It adds a START_AGAIN marker to the memory, indicating all operations before this point should be discarded and the pipeline rebuilt from scratch.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Reason for restarting the pipeline.",
            },
            output_type="dict - Contains the start_again signal and reason.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="The pipeline used UNION but should have used JOIN for tables with different schemas.")',
                    "description": "Signal that the pipeline should be restarted.",
                }
            ],
            user_metadata={"limitations": LIMITATION, "best_practices": BEST_PRACTICE},
        )

    def execute(self, query: str = "") -> Dict[str, Any]:
        """Add a START_AGAIN signal. No LLM call needed."""
        reason = query if query else "Pipeline restart requested by planner."

        return {
            "signal": "START_AGAIN",
            "reason": reason,
            "message": f"PIPELINE RESTART: All operations before this point should be discarded. Reason: {reason}",
        }


if __name__ == "__main__":
    tool = Start_Again_Tool()
    print(
        tool.execute(
            query="The pipeline incorrectly used UNION for tables with different schemas. Should use JOIN instead."
        )
    )
