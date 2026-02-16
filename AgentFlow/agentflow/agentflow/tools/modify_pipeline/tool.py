# agentflow/tools/modify_pipeline/tool.py

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


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Modify_Pipeline_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) By default it modifies the pipeline based on critique/sub-goal only; execution/scoring requires execute_pipeline mode.
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


def get_pipeline_critique_prompt(
    transformation_case_info: str, pipeline_plan: str
) -> str:
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


def get_pipeline_codegen_prompt(
    transformation_case_info: str,
    pipeline_plan: str,
    critique: str = "",
) -> str:
    """Generate prompt to convert modified pipeline into executable pandas code."""
    prompt = f"""
You are generating an executable Python script that implements a data-transformation pipeline using pandas.

You MUST implement the modified pipeline exactly (or apply critique fixes if critique indicates issues).

TRANSFORMATION CASE INFO (includes schemas/examples AND runtime constants):
{transformation_case_info}

MODIFIED PIPELINE PLAN TO IMPLEMENT:
{pipeline_plan}

CRITIQUE CONTEXT (if any):
{critique}

HARD REQUIREMENTS:
1) Output ONLY a single Python code block:
```python
<code>
```

The script must be directly executable (no placeholders).

Hints to be considered for Python code generation:
 - Your code should only take the "CSV file paths" given in the Source Data Information as inputs. [If Source name is Sourcex_y_z and its location is /path/to/test_z.csv, use the test_z.csv path!]
 - Please ensure all operation output contributed (or used) by the final output.
 - You may use string conversions or date conversions if needed. 
 - Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.
 - Make sure that table generated through the script has the same column structure as target.
 - Please answer what operation you should perform next based on "operation history", "source tables" and "target tables" information ("schema" as well as the "examples")  in one word.
 - If two source tables have different columns, DO NOT give the UNION operation.
 - If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
 - If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority.
 - If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
 - GROUP BY attribute(s) is(are) never of float types and it(they) often correspond(s) to the column(s) that has (have) all distinct/unique values in the target examples. These columns are usually at the leftmost part of the target schema. If you found a column in the target examples contain float values, do not include the column as GROUP BY attribute.
 - All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join)
 - Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have the same schema, such as C, and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM.
 - If duplicate tuples or duplicate keys exist in the target examples, no GROUP BY should be used.
 - If a column has integer values in one of the source tables, but the same column has float values in the target tables, an average aggregation should be applied to the column and the column should NOT be considered as GROUP BY attribute. 
 - Most source files have a numerical index column, which is always the first column, and it should be ignored in the transformation. Therefore, when reading a CSV file, please add index_col=0, e.g., sourceX = pd.read_csv('autopipeline-benchmarks/github-pipelines/lengthY_Z/test_X.csv', index_col=0)
 - Please look at the target examples, and ensure the generated data has the same type and name for each column in the target examples.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 - Please do not use source files that are not mentioned in this prompt.

Hint 1:
Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.

Hint 2:
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has more rows, it may indicate the following: (1) A Group By operator and Aggregate operators are missing. We would suggest adding a Group By operator using the left-most non-float, and unique attributes from the given target examples as GroupBy attributes and choosing the Aggregation operator such as count, average, medium, sum, etc., based on the range of valuesfor each of other columns. (2) If a Group By operator has been used, we would suggest remove some Group By attributes. (3) If OUTER join is used, it should be replaced by INNER join. (4) We shall remove rows that contain NaN values.

Hint 3:
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has fewer rows, it may indicate the following: (1) If INNER join is used, it should be replaced by OUTER join. (2) We shall keep rows that contain NaN values. (3) If Group By is used, it should be removed or use more Group By attributes.


Hint 4:
If multiple source tables share the same schema while the target table (i.e., target examples) also has the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key. 

Hint 5:
Group By columns are never float types. These Group By columns correspond to columns that are UNIQUE and non-float in the target examples, which are usually at the leftmost part of the columns of the target examples.

Hint 6:
If the given target examples contain duplicate keys or duplicate rows, Group By should NOT be used. 

Hint 7:
If the average value of a column in the target examples is significantly bigger than its average values in the source tables, sum aggregation should be applied to the column, and this column should be excluded from the Group By columns. 

Hint 8:
If a column that usually has value range (such as year or funded_year) in the target table has abnormal values (e.g., 0 or 16888 for year or XXXX_year), an aggregation should be applied to the column and this column MUST be EXCLUDED from the Group By columns.

Hint 9:
JOIN is usually applied to two tables sharing the same primary key, or applied to two tables where one table has a column (i.e., foreign key) referencing to the primary key of the other table.
If many source tables have different schemas (columns), look for a dimension table that has a lot of attributes and join it with each of the rest tables (aspect tables) on shared attributes. For example, test_5.csv has columns: ,Fecha,Mes,IdAhogado,IdPersona,Localidad,Provincia,CCAA,Hora,Latitud_inc,Longitud_inc,Sexo,Edad,Nacionalidad,Origen,Extraccion,Causa,TipoAhogamiento,Factor,Intervencion,Pronostico,Localizacion,Riesgo,Reanimacion,Vigilancia,Actividad,Deteccion,ID,Estacion,Estado,Latitud_est,Longitud_est,T_med,T_max,T_min,Precipitaciones,Presion,Dir. vi.,V_Viento,Nubosidad,ProfNievecm,InsolacHoras,Distancia, test_0.csv has columns ,IdOrigen,Origen, it means test_5 may join with test_0 on Origen. Then, test_1.csv has columns ,IdPronostico,Pronostico,Mortal, so test_5 will also join with test_1 on Pronostico. Similarly, test_5 will join with test_2 (IdDeteccion,Deteccion) on Deteccion, join with test_3 (IdTipo,TipoAhogamiento) on TipoAhogamiento, join with test_4 (IdInterv,Intervencion) on Intervencion, join with test_6 (IdActividad,Actividad) on Actividad, join with test_7 (IdCausa,Causa) on Causa, and join with test_8 (IdReanima,Reanimacion) on Reanimacion.

Hint 10:
Two different tables may join on shared columns that have different names. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host.

Hint 11:
All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join) 
- Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have exactly same schema, such as D and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM in one projection. No other processing is needed.

Hint 12:
No GROUP BY operator should be applied, if there is target examples have a single column or there is no primary key in the target examples. 

Hint 13:
IMPORTANT: NEVER use all target columns as the GROUP BY columns!!!

Hint 14:
If in the target data examples, many columns have constant values, use the same constant value in the Python script for those columns.

Hint 15: 
Consider applying string functions to certain columns that look similar but have different formats in the target and resulting data examples. 

Hint 16:
Please look at the target examples, and ensure the generated data has the same type and name for each column in the target examples.

Hint 17:
Most source files have a numerical index column, which is always the first column, and it should be ignored in the transformation. Therefore, when reading a CSV file, please add index_col=0, e.g., sourceX = pd.read_csv('autopipeline-benchmarks/github-pipelines/lengthY_Z/test_X.csv', index_col=0)


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


def get_pipeline_critique_with_score(
    transformation_case_info: str,
    pipeline_plan: str,
    code: str,
    score: Optional[float],
) -> str:
    score_text = "UNAVAILABLE" if score is None else f"{score:.6f}"
    prompt = f"""
You are reviewing a modified data-transformation pipeline using both design quality and execution score.

{transformation_case_info}

Proposed Pipeline:
{pipeline_plan}

Generated Code:
```python
{code}
```

Execution Score (0 to 3, higher is better; 3 is best): {score_text}

Use this score as an additional quality signal:
- Higher score means the generated output is closer to target behavior.
- Lower score suggests pipeline logic/operator choices are likely wrong.
- If score is UNAVAILABLE, critique based on pipeline and code only.

Return format:
$CRITIQUE:
Assessment: <CORRECT / PARTIALLY_CORRECT / INCORRECT>
Score: <numeric score or UNAVAILABLE>
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
            output_type="dict - Contains pipeline_id, modified pipeline definition, critique, and prompts; in execute_pipeline mode it also returns generated code, execution result, and score fields.",
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
        self.execute_pipeline = False

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

        if self.execute_pipeline:
            ground_truth_csv_path = _extract_ground_truth_csv_path(query)
            codegen_prompt = get_pipeline_codegen_prompt(
                query, modified_pipeline, critique
            )
            codegen_response = self.llm_engine(codegen_prompt)
            code_response = str(codegen_response)
            code = _extract_python_code(code_response) or code_response

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

                    try:
                        from auto_suggest_llm_util import (
                            calculate_Score as calculate_score_fn,
                        )
                    except Exception:
                        from auto_suggest_llm_util import (
                            calculate_score as calculate_score_fn,
                        )

                    score = float(
                        calculate_score_fn(ground_truth_df, generated_table_df)
                    )
                except Exception as exc:
                    score_error = str(exc)

            critique_prompt = get_pipeline_critique_with_score(
                query, modified_pipeline, code, score
            )
            critique_response = self.llm_engine(critique_prompt)
            new_critique = str(critique_response)

            return {
                "pipeline_id": pipeline_id,
                "pipeline": modified_pipeline,
                "critique": new_critique,
                "generated_code": code,
                "output_csv_path": output_csv_path,
                "ground_truth_csv_path": ground_truth_csv_path,
                "score": score,
                "score_error": score_error,
                "execution_error": execution_error,
                "execution_stdout": execution_stdout,
                "execution_stderr": execution_stderr,
            }

        # Step 2: Critique the modified pipeline
        critique_prompt = get_pipeline_critique_prompt(query, modified_pipeline)
        critique_response = self.llm_engine(critique_prompt)
        new_critique = str(critique_response)

        return {
            "pipeline_id": pipeline_id,
            "pipeline": modified_pipeline,
            "critique": new_critique,
        }


if __name__ == "__main__":
    tool = Modify_Pipeline_Tool(model_string="gpt-4.1-mini")
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
