# agentflow/tools/code_generator/tool.py

import re
from typing import Any, Dict, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Code_Generator_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It generates Python transformation code but does not execute it.
2) Generated code quality depends on the completeness and clarity of source/target information provided.
3) Complex multi-step transformations with many source tables may require iterative refinement.
4) It relies on the memory (action history) to understand prior pipeline steps; incomplete memory may lead to suboptimal code.
5) The generated code assumes pandas is available in the execution environment.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide the full query containing Target Table Name, Target Schema, Target Examples, and Source Information with file locations.
2) Ensure memory contains the complete action history so the tool can follow the correct sequence of operations.
3) Include any error messages from previous code generation attempts so the tool can correct mistakes.
4) Specify the CSV save path where the result should be written.
"""


def _extract_python_code(response: str) -> Optional[str]:
    """Extract Python code block from LLM response."""
    if not response:
        return None
    match = re.search(r"```[Pp]ython\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def get_code_generation_prompt(query: str, memory_actions: str, error_string: str) -> str:
    """Build the code generation prompt using the query (case info), memory actions, and error history."""
    prompt = f"""You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in the action history below. The code should be immediately executable in a correct way, which means it should NOT contain any placeholder for brevity. For example, even if there exist hundreds of source tables, these data need to be loaded completely one by one or in a programmable way.

    Transformation Context:

    {query}

    Action History (follow this sequence of operations strictly):
    {memory_actions}

    Based on the transformation context and action history, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omitting any single statement. For example, please list all the source paths that will be used.

    Please quote the Python script between one single "```Python" and "```".

    Hints to be considered for Python code generation:
 - Your code should only take the CSV file paths given in the Source Data Information as inputs.
 - Please ensure all operation output contributed (or used) by the final output.
 - You may use string conversions or date conversions if needed.
 - Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.
 - Make sure that table generated through the script has the same column structure as target.
 - Please answer what operation you should perform next based on the action history, source tables and target tables information (schema as well as the examples) in one word.
 - If two source tables have different columns, DO NOT give the UNION operation.
 - If there are multiple source tables and the target table having exactly same columns, give Union operation first priority.
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
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has more rows, it may indicate the following: (1) A Group By operator and Aggregate operators are missing. We would suggest adding a Group By operator using the left-most non-float, and unique attributes from the given target examples as GroupBy attributes and choosing the Aggregation operator such as count, average, medium, sum, etc., based on the range of values for each of other columns. (2) If a Group By operator has been used, we would suggest remove some Group By attributes. (3) If OUTER join is used, it should be replaced by INNER join. (4) We shall remove rows that contain NaN values.

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

 Errors in previous attempts: {error_string}
"""
    return prompt


class Code_Generator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description=(
                "A tool that generates executable Python transformation code based on the "
                "transformation query (target/source table information) and the action history "
                "from memory. It produces a complete pandas-based Python script that converts "
                "source tables into the target table format. The tool generates code only and "
                "does not execute it."
            ),
            tool_version="1.0.0",
            input_types={
                "query": "str - The full transformation context including Target Table Name, Target Schema, Target Examples, Source Information with file locations, and CSV save path.",
                "memory_actions": "str - (Optional) The action history from memory describing prior pipeline operations. Defaults to empty.",
                "error_string": "str - (Optional) Error messages from previous code generation attempts for iterative correction. Defaults to empty.",
            },
            output_type="dict - A dictionary containing the generated Python code, the raw LLM response, and the prompt used.",
            demo_commands=[
                {
                    "command": (
                        'execution = tool.execute(query="1. Target Table Name: Target1_0\\n'
                        '2. Target Schema: [\'State\': string, \'AverageTemperature\': float]\\n'
                        '3. Target Examples: ...\\n4. Source Information: ...\\n'
                        '5. Write the result to this path output.csv")'
                    ),
                    "description": "Generate Python transformation code from transformation case information.",
                },
                {
                    "command": (
                        'execution = tool.execute('
                        'query="1. Target Table Name: Target4_31\\n...", '
                        'memory_actions="Action Step 1: {\'tool_name\': \'Configure_Join_Operator_Tool\', ...}", '
                        'error_string="KeyError: \'County\'"'
                        ')'
                    ),
                    "description": "Generate code with action history and error correction context.",
                },
            ],
            user_metadata={"limitations": LIMITATION, "best_practices": BEST_PRACTICE},
        )

        print(f"Initializing Code_Generator_Tool with model_string: {model_string}")

        # NOTE: deterministic mode
        self.llm_engine = create_llm_engine(
            model_string=model_string,
            is_multimodal=False,
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

    def execute(self, query: str = "", memory_actions: str = "", error_string: str = "") -> Dict[str, Any]:
        """
        Generate Python transformation code based on the query and action history.

        Parameters:
            query (str): The full transformation context (target table info, source info, save path).
            memory_actions (str): The action history from memory describing prior operations.
            error_string (str): Error messages from previous attempts for iterative correction.

        Returns:
            dict: A dictionary containing:
                - 'generated_code': The extracted Python code (or None if extraction failed)
                - 'raw_response': The full LLM response
                - 'prompt': The prompt that was sent to the LLM
        """
        if not self.llm_engine:
            raise ValueError(
                "LLM engine not initialized. Please provide a valid model_string when initializing the tool."
            )

        if not query:
            raise ValueError(
                "query parameter is required and must contain transformation case information."
            )

        # Build the code generation prompt
        full_prompt = get_code_generation_prompt(
            query=query,
            memory_actions=memory_actions if memory_actions else "No prior actions.",
            error_string=error_string if error_string else "No previous errors.",
        )

        # Call the LLM engine
        response = self.llm_engine(full_prompt)
        response_str = str(response)

        # Extract Python code from the response
        generated_code = _extract_python_code(response_str)

        return {
            "generated_code": generated_code,
            "raw_response": response_str,
            "prompt": full_prompt,
        }

    def get_metadata(self):
        """Returns the metadata for the Code_Generator_Tool."""
        metadata = super().get_metadata()
        metadata["require_llm_engine"] = self.require_llm_engine
        return metadata


if __name__ == "__main__":
    # Test command:
    """
    Run the following commands in the terminal to test the script:

    cd agentflow/tools/code_generator
    python tool.py
    """

    tool = Code_Generator_Tool(model_string="gpt-4o")

    # Get tool metadata
    metadata = tool.get_metadata()
    print("Tool Metadata:", metadata)

    # Sample query
    sample_query = """1. Target Table Name: Target4_31
2. Target Schema: ['County': string, 'm1401': string, 'm1402': string, 'm1403': string, 'm1404': string]
3. Target Examples: There are 17 available target examples:          County       m1401       m1402       m1403       m1404
10      El Paso  $4,923,633  $5,116,438  $5,929,766  $5,535,184
4. Source Information:
    Source 0 Name: Source4_31_0
    Source 0 Schema: ['County', 'm1403']
    Source 0 File Location: autopipeline-benchmarks/github-pipelines/length4_31/test_0.csv
    Source 1 Name: Source4_31_1
    Source 1 Schema: ['County']
    Source 1 File Location: autopipeline-benchmarks/github-pipelines/length4_31/test_1.csv
5. Write the result to this path output.csv"""

    sample_memory = """Action Step 1: {'tool_name': 'Configure_Join_Operator_Tool', 'sub_goal': 'Configure join between source tables', 'command': 'tool.execute(query=...)', 'result': {'join_spec': [['test_0.csv', 'test_2.csv'], ['test_0.County', 'test_2.County']]}}"""

    print("\n### Testing Code Generation ###")
    try:
        execution = tool.execute(
            query=sample_query,
            memory_actions=sample_memory,
            error_string="",
        )
        print("\n### Generated Code:")
        print(execution["generated_code"])
    except ValueError as e:
        print(f"Execution failed: {e}")

    print("\nDone!")
