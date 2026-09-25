# agentflow/tools/Refine_Existing_Pipeline/tool.py

import os
import re
import subprocess
import sys
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

from hints.hints_static import get_hints_section, CRITIQUE_HINT_IDS


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Refine_Existing_Pipeline"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) By default it refines the pipeline based on self-analysis only; execution/scoring requires execute_pipeline mode.
2) It requires a valid pipeline_id referencing a previously created pipeline.
3) If the original pipeline or execution context are unclear, corrections may be suboptimal.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide the pipeline_id of the pipeline to refine.
2) Include the full transformation case info and the current pipeline definition.
3) Pass execution context (error messages, score, intermediate schemas) to help the tool self-diagnose.
"""


def get_refine_pipeline_prompt(
    transformation_case_info: str,
    current_pipeline: str,
    execution_context: str = "",
) -> str:
    """Generate a single combined prompt for pipeline critique and correction."""
    execution_section = ""
    if execution_context:
        execution_section = f"""
Execution Context (error messages / score / intermediate output):
{execution_context}
"""
    prompt = f"""
You are critiquing a data-pipeline that transforms multiple source tables to follow the schema of the target table. An LLM agent has created this pipeline plan and generated Python code. Review the current pipeline and suggest corrections, then provide the corrected pipeline plan and executable code.

{transformation_case_info}

Current Pipeline:
{current_pipeline}
{execution_section}
Your task:
1. Identify what is wrong with the current pipeline (if anything).
2. Specify what steps need to be added, changed, or removed.
3. Output the CORRECTED pipeline plan.
4. Generate the executable Python script for the corrected pipeline. The code must be immediately executable — no placeholders.

{get_hints_section(CRITIQUE_HINT_IDS, fmt="numbered")}

Output format:
$CRITIQUE: <your detailed analysis of what is wrong and what should change>$

$PIPELINE:
Step 1: <OPERATION_TYPE> - <configuration details>
Step 2: <OPERATION_TYPE> - <configuration details>
...
$

Please quote the Python script between one single "```Python" and "```".
    """
    return prompt


def _extract_python_code(response: str) -> Optional[str]:
    if not response:
        return None
    match = re.search(r"```[Pp]ython\s*(.*?)\s*```", response, re.DOTALL)
    return match.group(1).strip() if match else None


def _extract_output_csv_path(generated_code: str) -> Optional[str]:
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
    if to_csv_matches:
        return to_csv_matches[-1]

    # Handle: var = "/path/to/output.csv" followed by df.to_csv(var)
    for var_match in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+\.csv)["\']', generated_code):
        var_name, csv_path = var_match.group(1), var_match.group(2)
        if re.search(rf'\.to_csv\s*\(\s*{re.escape(var_name)}\b', generated_code):
            return csv_path

    return None


def _extract_ground_truth_csv_path(query: str) -> Optional[str]:
    if not query:
        return None

    explicit_match = re.search(
        r'GROUND_TRUTH_CSV_PATH\s*=\s*["\']([^"\']+\.csv)["\']', query
    )
    if explicit_match:
        return explicit_match.group(1)

    case_match = re.search(
        r"(autopipeline-benchmarks/[^/]+-pipelines/length\d+_\d+)/test_\d+\.csv",
        query,
    )
    if case_match:
        return f"{case_match.group(1)}/target.csv"

    return None


def _resolve_path(path_str: Optional[str]) -> Optional[str]:
    if not path_str:
        return None
    return path_str if os.path.isabs(path_str) else str(_TRANSCHEMA_ROOT / path_str)


def _get_script_archive_dir(
    ground_truth_csv_path: Optional[str], fallback_dir: Optional[str]
) -> Path:
    resolved_ground_truth = _resolve_path(ground_truth_csv_path)
    if resolved_ground_truth:
        gt_path = Path(resolved_ground_truth)
        if gt_path.is_file() or gt_path.suffix.lower() == ".csv":
            return gt_path.parent / "script_archive"
    if fallback_dir:
        return Path(fallback_dir)
    return _TRANSCHEMA_ROOT / "AgentFlow" / "solver_cache"


class Refine_Existing_Pipeline(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that critiques and corrects an existing data transformation pipeline in a single LLM call. Analogous to the operator-level Critique_Pipeline_Tool but at pipeline level: it receives the current pipeline and execution context, self-diagnoses issues, and produces a corrected pipeline plan plus executable code.",
            tool_version="1.0.0",
            input_types={
                "query": "str - Transformation case information including Target Table, Source Information.",
                "pipeline_id": "str - The ID of the pipeline to refine (from a previous Create_New_Pipeline result).",
                "current_pipeline": "str - The current pipeline definition to critique and correct.",
                "execution_context": "str - Optional. Score feedback, error messages, or intermediate output to aid self-diagnosis.",
            },
            output_type="dict - Contains pipeline_id, corrected pipeline definition, critique, generated_code, and (when execute_pipeline=True) execution and score fields.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="1. Target Table Name: Target1_0\\n...", pipeline_id="pipeline_abc123", current_pipeline="Step 1: UNION ...", execution_context="Score: 0.5\\nError: wrong row count")',
                    "description": "Critique and correct an existing pipeline.",
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

    def execute(
        self,
        query: str = "",
        pipeline_id: str = "",
        current_pipeline: str = "",
        execution_context: str = "",
    ) -> Dict[str, Any]:
        """Critique and correct an existing pipeline in a single LLM call."""
        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information"
            )
        if not pipeline_id:
            raise ValueError(
                "pipeline_id parameter is required to identify which pipeline to refine"
            )

        # Single LLM call: critique + corrected plan + corrected code
        response_str = str(
            self.llm_engine(
                get_refine_pipeline_prompt(query, current_pipeline, execution_context)
            )
        )

        # Parse $CRITIQUE:...$ block
        critique_match = re.search(r"\$CRITIQUE:(.*?)\$", response_str, re.DOTALL)
        critique = critique_match.group(1).strip() if critique_match else ""

        # Parse $PIPELINE:...$ block
        pipeline_match = re.search(r"\$PIPELINE:(.*?)\$", response_str, re.DOTALL)
        corrected_pipeline = pipeline_match.group(1).strip() if pipeline_match else response_str

        # Parse ```python...``` block
        code = _extract_python_code(response_str) or ""

        if not self.execute_pipeline:
            return {
                "pipeline_id": pipeline_id,
                "pipeline": corrected_pipeline,
                "critique": critique,
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
            "pipeline": corrected_pipeline,
            "critique": critique,
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
    tool = Refine_Existing_Pipeline(model_string="gpt-4.1-mini")
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
            execution_context="Score: 0.0\nError: Source tables have different schemas, UNION is invalid.",
        )
    )
