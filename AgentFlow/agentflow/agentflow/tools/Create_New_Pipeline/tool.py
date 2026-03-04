# agentflow/tools/Create_New_Pipeline/tool.py

import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


_TRANSCHEMA_ROOT = Path(__file__).resolve().parents[5]
if str(_TRANSCHEMA_ROOT) not in sys.path:
    sys.path.insert(0, str(_TRANSCHEMA_ROOT))

_EVAL_SCORE_ROOT = str(_TRANSCHEMA_ROOT / "eval_score")
if _EVAL_SCORE_ROOT not in sys.path:
    sys.path.insert(0, _EVAL_SCORE_ROOT)

from hints.hints_static import get_hints_section, PIPELINE_HINT_IDS


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Create_New_Pipeline"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) The quality of the pipeline depends on how representative the provided target examples are.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide complete target and source schemas with representative examples.
2) Include all source table information so the tool can reason about the full pipeline.
3) Use this tool at the start to design the overall pipeline before configuring individual operators.
"""


def get_pipeline_prompt(transformation_case_info: str) -> str:
    """Generate a single combined prompt for pipeline design and code generation."""
    prompt = f"""
You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code must be immediately executable in a correct way, which means it should NOT contain any placeholder for brevity. For example, even if there exist hundreds of source tables, these data need to be loaded completely one by one or in a programmable way. Before generating the code, think step by step about the full transformation plan.

{transformation_case_info}

STEP 1 — Think step by step about the full pipeline:
  a) What operations (JOIN/UNION/GROUP_BY/AGGREGATE/PIVOT/UNPIVOT) are needed and in what order?
  b) What columns appear in the target but need aggregation from source?
  c) Are all source tables used?

STEP 2 — Output the complete pipeline plan:
$PIPELINE:
Step 1: <OPERATION_TYPE> - <configuration details>
Step 2: <OPERATION_TYPE> - <configuration details>
...
$

STEP 3 — Generate the executable Python script implementing the plan above.
The code must be immediately executable — no placeholders. Load all source CSV files listed in the source information.
Please quote the Python script between one single "```Python" and "```".

{get_hints_section(PIPELINE_HINT_IDS, fmt="numbered")}
    """
    return prompt


def _extract_python_code(response: str) -> Optional[str]:
    """Extract Python code block from an LLM response."""
    if not response:
        return None
    match = re.search(r"```[Pp]ython\s*(.*?)\s*```", response, re.DOTALL)
    return match.group(1).strip() if match else None


def _extract_output_csv_path(generated_code: str) -> Optional[str]:
    """Extract output CSV path from code via OUTPUT_CSV_PATH assignment or to_csv call."""
    if not generated_code:
        return None

    assignment_match = re.search(
        r'OUTPUT_CSV_PATH\s*=\s*["\']([^"\']+\.csv)["\']', generated_code
    )
    if assignment_match:
        return assignment_match.group(1)

    to_csv_matches = re.findall(
        r"\.to_csv\s*\(\s*['\"]([^'\"]+\.csv)['\"]", generated_code
    )
    return to_csv_matches[-1] if to_csv_matches else None


def _extract_ground_truth_csv_path(query: str) -> Optional[str]:
    """Extract ground-truth CSV path from explicit constant or case identifiers in query."""
    if not query:
        return None

    explicit_match = re.search(
        r'GROUND_TRUTH_CSV_PATH\s*=\s*["\']([^"\']+\.csv)["\']', query
    )
    if explicit_match:
        return explicit_match.group(1)

    case_match = re.search(
        r"(autopipeline-benchmarks/github-pipelines/length\d+_\d+)/test_\d+\.csv",
        query,
    )
    if case_match:
        return f"{case_match.group(1)}/target.csv"

    target_name_match = re.search(r"Target Table Name:\s*Target(\d+_\d+)", query)
    if target_name_match:
        case_id = target_name_match.group(1)
        return f"autopipeline-benchmarks/github-pipelines/length{case_id}/target.csv"

    return None


def _resolve_path(path_str: Optional[str]) -> Optional[str]:
    """Resolve path relative to repository root when needed."""
    if not path_str:
        return None
    return path_str if os.path.isabs(path_str) else str(_TRANSCHEMA_ROOT / path_str)


def _get_script_archive_dir(
    ground_truth_csv_path: Optional[str], fallback_dir: Optional[str]
) -> Path:
    """Return case-local script archive directory when possible."""
    resolved_ground_truth = _resolve_path(ground_truth_csv_path)
    if resolved_ground_truth:
        gt_path = Path(resolved_ground_truth)
        if gt_path.is_file() or gt_path.suffix.lower() == ".csv":
            return gt_path.parent / "script_archive"
    if fallback_dir:
        return Path(fallback_dir)
    return _TRANSCHEMA_ROOT / "AgentFlow" / "solver_cache"


class Create_New_Pipeline(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4.1-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that designs a complete data transformation pipeline from scratch. In a single LLM call it plans the full sequence of operations (JOIN, UNION, GROUP_BY/AGGREGATE, etc.) and generates the executable Python code. Returns a pipeline_id, the pipeline definition, and the generated code.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table, Source Information, and any relevant context.",
            },
            output_type="dict - Contains pipeline_id, pipeline definition (sequence of operations), generated_code, and (when execute_pipeline=True) execution and score fields.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n2. Target Schema: [State: string, AverageTemperature: float]\\n3. Target Examples: ...\\n4. Source Information: ...")',
                    "description": "Design a complete pipeline and generate code for a transformation case.",
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
        self.execute_pipeline = False

    def execute(self, query: str = "") -> Dict[str, Any]:
        """Design a new pipeline and generate executable code in a single LLM call."""
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information"
            )

        pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"

        # Single LLM call: pipeline design + code generation
        response_str = str(self.llm_engine(get_pipeline_prompt(query)))

        # Parse $PIPELINE:...$ block
        pipeline_match = re.search(r"\$PIPELINE:(.*?)\$", response_str, re.DOTALL)
        pipeline_plan = pipeline_match.group(1).strip() if pipeline_match else response_str

        # Parse ```python...``` block
        code = _extract_python_code(response_str) or ""

        if not self.execute_pipeline:
            return {
                "pipeline_id": pipeline_id,
                "pipeline": pipeline_plan,
                "generated_code": code,
            }

        # Execute and score
        ground_truth_csv_path = _extract_ground_truth_csv_path(query)
        output_csv_path = _extract_output_csv_path(code)
        if not output_csv_path:
            output_csv_path = str(
                Path(
                    self.output_dir
                    or str(_TRANSCHEMA_ROOT / "AgentFlow" / "solver_cache")
                )
                / f"{pipeline_id}_output.csv"
            )

        script_dir = _get_script_archive_dir(
            ground_truth_csv_path=ground_truth_csv_path,
            fallback_dir=self.output_dir,
        )
        script_dir.mkdir(parents=True, exist_ok=True)
        script_path = script_dir / "agent_run.py"
        script_path.write_text(code)

        execution_error = None
        execution_stdout = ""
        execution_stderr = ""
        score = None
        score_fd = None
        column_mapping_score = None
        score_details = None
        score_error = None

        try:
            proc = subprocess.run(
                [sys.executable, str(script_path.resolve())],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(_TRANSCHEMA_ROOT),
            )
            execution_stdout = proc.stdout[-2000:] if proc.stdout else ""
            execution_stderr = proc.stderr[-2000:] if proc.stderr else ""
            if proc.returncode != 0:
                execution_error = (
                    execution_stderr
                    or "Unknown error while executing generated pipeline code."
                )
        except subprocess.TimeoutExpired:
            execution_error = "Code execution timed out after 120 seconds."
        except Exception as exc:
            execution_error = str(exc)

        resolved_output_csv_path = _resolve_path(output_csv_path)
        resolved_ground_truth_csv_path = _resolve_path(ground_truth_csv_path)

        if (
            execution_error is None
            and resolved_output_csv_path
            and resolved_ground_truth_csv_path
            and os.path.isfile(resolved_output_csv_path)
            and os.path.isfile(resolved_ground_truth_csv_path)
        ):
            try:
                ground_truth_df = pd.read_csv(
                    resolved_ground_truth_csv_path, index_col=0, low_memory=False
                )
                generated_table_df = pd.read_csv(
                    resolved_output_csv_path, low_memory=False
                )
                unnamed_cols = [
                    col
                    for col in generated_table_df.columns
                    if str(col).startswith("Unnamed")
                ]
                if unnamed_cols:
                    generated_table_df = generated_table_df.drop(
                        columns=unnamed_cols
                    )

                from score import relative_csv_score, summarize_score

                (
                    fd_ratio,
                    col_ratio,
                    combined_score,
                    fd_f1,
                    true_combined_score,
                    debug_dict,
                ) = relative_csv_score(generated_table_df, ground_truth_df)

                score = float(true_combined_score)
                score_fd = float(fd_f1)
                column_mapping_score = float(col_ratio)
                score_details = summarize_score(debug_dict, true_combined_score, fd_f1, col_ratio)
            except Exception as exc:
                score_error = str(exc)

        return {
            "pipeline_id": pipeline_id,
            "pipeline": pipeline_plan,
            "generated_code": code,
            "output_csv_path": output_csv_path,
            "ground_truth_csv_path": ground_truth_csv_path,
            "score": score,
            "score_fd": score_fd,
            "column_mapping_score": column_mapping_score,
            "score_details": score_details,
            "score_error": score_error,
            "execution_error": execution_error,
            "execution_stdout": execution_stdout,
            "execution_stderr": execution_stderr,
        }


if __name__ == "__main__":
    tool = Create_New_Pipeline(model_string="gpt-4o-mini")
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
