# agentflow/tools/add_operator/tool.py

import ast
import re
from typing import Any, Dict, List, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Add_Operator_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) The decision quality depends on the provided operation history, schema, and examples.
2) It selects only the next high-level operator (JOIN/UNION/GROUP_BY/AGGREGATE/PIVOT/UNPIVOT/NO_MORE_OPERATION), not the full pipeline.
3) If the target semantics cannot be inferred from examples, it may return an uncertain choice.
4) It does not execute transformations; it only proposes the next operator.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide complete target schema and representative target examples.
2) Provide all source schemas and examples (and file paths if available).
3) Provide accurate operation history (including configs) to avoid repeating steps.
4) If intermediate results exist, provide them so the tool can reason about the current state.
"""


def _extract_between_dollars(text: str) -> Optional[str]:
    """Extract the first token enclosed in $...$."""
    if not text:
        return None
    m = re.search(r"\$(.*?)\$", text, flags=re.DOTALL)
    if not m:
        return None
    return m.group(1).strip()


def _parse_case_from_query_text(query: str) -> Dict[str, Any]:
    """Best-effort parser for the common case block inserted into the query."""
    res: Dict[str, Any] = {}
    if not query:
        return res

    # Operation History: [...] or Operation History (..): ...
    m = re.search(r"Operation History\s*:\s*(\[[^\]]*\])", query)
    if m:
        res["operation_history_str"] = m.group(1).strip()

    # Target name
    m = re.search(r"Target Table Name\s*:\s*([^\n]+)", query)
    if not m:
        m = re.search(r"Target Table\s*:\s*\n\s*-\s*Name\s*:\s*([^\n]+)", query)
    if m:
        res["target_data_name"] = m.group(1).strip()

    # Target schema
    m = re.search(r"Target Schema\s*:\s*([^\n]+)", query)
    if not m:
        m = re.search(r"-\s*Schema\s*:\s*([^\n]+)", query)
    if m:
        res["target_data_schema"] = m.group(1).strip()

    # Target examples: capture a block until Source Tables or Source Information
    m = re.search(
        r"Target Examples\s*:(.*?)(?:\n\s*Source Tables\s*:|\n\s*Source Information\s*:|\n\s*Source Tables\b)",
        query,
        flags=re.DOTALL,
    )
    if m:
        res["target_samples"] = m.group(1).strip()

    # Source information block: from Source Tables/Source Information to Decision/Decision to make/end
    m = re.search(
        r"(?:Source Tables\s*:|Source Information\s*:)(.*?)(?:\n\s*Decision to make\s*:|\n\s*Decision\s*:|\Z)",
        query,
        flags=re.DOTALL,
    )
    if m:
        res["source_information"] = m.group(1).strip()

    return res


def get_next_operator_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    fd_hints,
    hints,
    all_intermediate_results: dict = {},
):
    prompt_start = f"""
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer \"what operation should be performed next?\". Take this decision based on \"operation history\", the schema of the source, target tables, and examples in the target table.
Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Source Information: {source_information}

"""
    if not all_intermediate_results:
        prompt_middle = ""
    else:
        subprompts_middle = []
        for i, op in enumerate(operation_history):
            step = i + 1
            if step not in all_intermediate_results:
                continue
            interm = all_intermediate_results[step]
            # Accept either objects (with .schema/.source_samples_string) or dicts
            schema = getattr(interm, "schema", None) or interm.get("schema", "")
            samples = getattr(interm, "source_samples_string", None) or interm.get(
                "source_samples_string", ""
            )
            subprompts_middle.append(
                f"After the {step}st/nd/rd/th operation {op}, the intermediate table is named 'intermediate_step{step}'.\nThe intermediate table schema is as follows: \n{schema} \nExamples: {samples}"
            )
        prompt_middle = "\n".join(subprompts_middle)

    prompt_last = f"""

{fd_hints}

{hints[0] if isinstance(hints, list) and len(hints) > 0 else hints}


- Please answer what operation you should perform next based on \"operation history\", \"source tables\" and \"target tables\" information (\"schema\" as well as the \"examples\")  in one word.
- If any two source tables have different columns, DO NOT give the UNION operation.
- If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
- If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority. 
- Note that some column names, e.g., purpose, may not match the values in the column, in this case consider the column to be aggregation, e.g., count per purpose. 
- If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
- If the given target examples contain duplicate keys or duplicate tuples, Group By should NOT be used.
- All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join)
- Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have the same schema, such as C, and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM.
- Two tables may join on columns that have different names but similar values. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host. Furthermore, if test_2 contains a column Host City including values such as Paris, Bern, Albany, Berlin, and test_3 contains a column City also contains city names, they should be joined on HostCity=City.  
- Please try to make sure, using the operator history, that ALL THE COLUMNS IN THE TARGET TABLE ARE ACCOUNTED FOR.
- If you feel no more operation is needed further, please return 'NO_MORE_OPERATION'.
- You should only answer from allowed operations.
- Try not to repeat operation and it's configuration from the operation history.
- the final answer should be in $ quotes. i.e. $OPERATOR$"""
    full_prompt = f"{prompt_start}{prompt_middle}{prompt_last}"
    return [full_prompt]


class Add_Operator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that decides what high-level operator should be performed next in a data transformation pipeline.",
            tool_version="1.0.0",
            input_types={
                "query": "str - (Optional) A full case description. If provided, the tool will attempt to parse target/source/history.",
                "allowed_operation_list": "list[str] - Allowed operations. If omitted, defaults to standard operator list.",
                "operation_history": "list[str] - List of previously applied operations.",
                "target_data_name": "str - Target table name.",
                "target_data_schema": "str - Target schema.",
                "target_samples": "str - Target examples / sample rows.",
                "file_count": "int - Number of source files (optional).",
                "source_information": "str - Source tables info (schema, examples, file paths).",
                "fd_hints": "str - FD or other hints (optional).",
                "hints": "list[str] - Additional hints (optional).",
                "all_intermediate_results": "dict - Intermediate results keyed by step (optional).",
            },
            output_type="dict - Contains the selected operator (or NO_MORE_OPERATION), plus raw LLM response and prompt.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Operation History: []\nTarget Table Name: Target1_0\nTarget Schema: [State: string, AverageTemperature: float]\nTarget Examples: State AverageTemperature\\nZhejiang 16.18\nSource Information: Source 0 Name: Source1_0_0 Schema: [dt, AverageTemperature, AverageTemperatureUncertainty, State, Country]")',
                    "description": "Decide the next operator from an inline case description.",
                }
            ],
            user_metadata={"limitations": LIMITATION, "best_practices": BEST_PRACTICE},
        )

        # NOTE: deterministic mode
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
        allowed_operation_list: Optional[List[str]] = None,
        operation_history: Optional[List[str]] = None,
        target_data_name: Optional[str] = None,
        target_data_schema: Optional[str] = None,
        target_samples: Optional[str] = None,
        file_count: Optional[int] = None,
        source_information: Optional[str] = None,
        fd_hints: str = "",
        hints: Optional[List[str]] = None,
        all_intermediate_results: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Run the operator-selection prompt and return the chosen operator."""

        # Defaults
        if allowed_operation_list is None:
            allowed_operation_list = [
                "JOIN",
                "UNION",
                "GROUP_BY/AGGREGATE",
                "PIVOT",
                "UNPIVOT",
                "NO_MORE_OPERATION",
            ]
        if operation_history is None:
            operation_history = []
        if hints is None:
            hints = [""]
        if all_intermediate_results is None:
            all_intermediate_results = {}

        # If key fields are missing, try to parse from the free-form query.
        if query and (
            target_data_name is None
            or target_data_schema is None
            or target_samples is None
            or source_information is None
        ):
            parsed = _parse_case_from_query_text(query)
            target_data_name = target_data_name or parsed.get("target_data_name")
            target_data_schema = target_data_schema or parsed.get("target_data_schema")
            target_samples = target_samples or parsed.get("target_samples")
            source_information = source_information or parsed.get("source_information")

            # Parse operation history if provided as a literal list
            if operation_history == [] and parsed.get("operation_history_str"):
                try:
                    operation_history = ast.literal_eval(parsed["operation_history_str"])  # type: ignore[name-defined]
                except Exception:
                    pass

        # Hard fallback: keep prompt running even if some fields are missing
        target_data_name = target_data_name or ""
        target_data_schema = target_data_schema or ""
        target_samples = target_samples or ""
        source_information = source_information or ""

        full_prompt = get_next_operator_prompt(
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples=target_samples,
            file_count=file_count,
            source_information=source_information,
            fd_hints=fd_hints,
            hints=hints,
            all_intermediate_results=all_intermediate_results,
        )[0]

        response = self.llm_engine(full_prompt)
        operator = _extract_between_dollars(str(response)) or str(response).strip()

        return {
            "operator": operator,
            "raw_response": str(response),
            "prompt": full_prompt,
        }


if __name__ == "__main__":
    # Minimal smoke test (requires a configured LLM engine / API key)
    tool = Add_Operator_Tool(model_string="gpt-4o-mini")
    case_query = """
Operation History: []

Target Table Name: Target1_0
Target Schema: ['State': string, 'AverageTemperature': float]
Target Examples: There are 241 available target examples:            State  AverageTemperature
240     Zhejiang           16.185409
116  Mato Grosso           25.471903
41      Dagestan            9.737170

Source Information:
Source 0 Name: Source1_0_0
Source 0 Schema: ['dt', 'AverageTemperature', 'AverageTemperatureUncertainty', 'State', 'Country']
Source 0 Examples:
dt  AverageTemperature  AverageTemperatureUncertainty  State  Country
2002-11-01  4.190  0.187  Rostov  Russia
""".strip()

    print(tool.execute(query=case_query))
