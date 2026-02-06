# agentflow/tools/configure_group_by_aggregate_operator/tool.py

import ast
import re
from typing import Any, Dict, List, Optional, Tuple

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


TOOL_NAME = "Configure_GroupBy_Aggregate_Operator_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It proposes GroupBy/Aggregate columns and functions based on schemas/examples and may be ambiguous.
2) It does not execute aggregations; it only suggests the configuration.
3) If the target examples are not representative, aggregation choices may be incorrect.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide representative target examples (to infer whether SUM/AVG/COUNT etc. is needed).
2) Provide full source schemas and examples.
3) Include operation history so the tool doesn't repeat an existing GroupBy config.
4) Provide FD hints when available.
"""


def _extract_between_dollars(text: str) -> Optional[str]:
    if not text:
        return None
    m = re.search(r"\$(.*?)\$", text, flags=re.DOTALL)
    if not m:
        return None
    return m.group(1).strip()


def _parse_case_from_query_text(query: str) -> Dict[str, Any]:
    res: Dict[str, Any] = {}
    if not query:
        return res

    m = re.search(r"Operation History\s*:\s*(\[[^\]]*\])", query)
    if m:
        res["operation_history_str"] = m.group(1).strip()

    m = re.search(r"Target Table Name\s*:\s*([^\n]+)", query)
    if m:
        res["target_data_name"] = m.group(1).strip()

    m = re.search(r"Target Schema\s*:\s*([^\n]+)", query)
    if m:
        res["target_data_schema"] = m.group(1).strip()

    m = re.search(
        r"Target Examples\s*:(.*?)(?:\n\s*Source Tables\s*:|\n\s*Source Information\s*:|\Z)",
        query,
        flags=re.DOTALL,
    )
    if m:
        res["target_samples"] = m.group(1).strip()

    m = re.search(
        r"(?:Source Tables\s*:|Source Information\s*:)(.*?)(?:\n\s*Decision to make\s*:|\Z)",
        query,
        flags=re.DOTALL,
    )
    if m:
        res["source_information"] = m.group(1).strip()

    return res


def _extract_group_by_and_aggs(payload: str) -> Tuple[Optional[Any], Optional[Any]]:
    """Parse either a dict-like answer or the: group_by = [...], aggregations = [...] format."""
    if not payload:
        return None, None

    # Try dict parsing first
    if payload.strip().startswith("{"):
        try:
            obj = ast.literal_eval(payload)
            if isinstance(obj, dict):
                return obj.get("group_by"), obj.get("aggregations")
        except Exception:
            pass

    # Try regex extraction of lists
    gb_match = re.search(r"group_by\"?\s*=\s*(\[[\s\S]*?\])", payload)
    agg_match = re.search(r"aggregations\"?\s*=\s*(\[[\s\S]*?\])", payload)

    group_by = None
    aggs = None
    if gb_match:
        try:
            group_by = ast.literal_eval(gb_match.group(1))
        except Exception:
            group_by = gb_match.group(1)
    if agg_match:
        try:
            aggs = ast.literal_eval(agg_match.group(1))
        except Exception:
            aggs = agg_match.group(1)

    return group_by, aggs


def get_group_by_aggregate_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    hints,
    fd_hints,
):
    prompt = """
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "1. Which columns should be used for Group By operation? 2. Which columns should be Aggregated? 3.Which Aggregation functions should be used?". Take this decision based on "Operation History", few-shot-examples, "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.


1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}


-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}

- Please answer on which columns "Group By" operation should be performed, on which columns aggregation should be performed and which aggregation functions should be used. 
- GroupBy columns should NEVER have float types in the given target examples. These GroupBy columns always contain UNIQUE and integer or string values in the given target examples. GroupBy columns are usually at the leftmost part of the columns of target examples.
- If a column is part of a group by operation, it will NOT be part of an aggregation operation.
- Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.
- If many columns in the target table have similar integer values, it probably suggests a count aggregation should be used. 
- If a column (such as user_id or age) has float values (such as 1211.2234 or 33.17) in the given target examples, while having integer values (such as 1001 or 35) in the given source tables, it suggests that an "average" aggregation should be applied to the column, no matter whether the column sounds like an ID. Importantly, this column MUST BE EXCLUDED from the GroupBy columns.
- If a column that usually has value ranges (such as year or funded_year) in the target table has abnormal values (e.g., 0 or > 3000 for year or XXXX_year), an aggregation should be applied to the column. Then, this column MUST be EXCLUDED from the Group By columns. 
- If in the target data examples, many columns have similar but different numerical values such as 5 5 4 5 4, in each row, it indicates that a COUNT DISTINCT is used.
- You should only answer from available columns of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in the following format. lists where first list should be group by columns, next list should cover aggregation function and on which columns aggregations should be performed.
- Example : "group_by" = [table_name.group_by_column1, table_name.group_by_column_2, ...], "aggregations" = [aggregation_function1(table_name.aggregation_column), aggregation_function2(table_name.aggregation_column), ...]
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        hints=hints,
        fd_hints=fd_hints,
    )
    return [prompt]


class Configure_GroupBy_Aggregate_Operator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that configures a GROUP_BY/AGGREGATE operator (group-by columns, aggregation columns, and aggregation functions).",
            tool_version="1.0.0",
            input_types={
                "query": "str - (Optional) A full case description. If provided, the tool will attempt to parse target/source/history.",
                "allowed_operation_list": "list[str] - Allowed operations (optional).",
                "operation_history": "list[str] - List of previously applied operations.",
                "target_data_name": "str - Target table name.",
                "target_data_schema": "str - Target schema.",
                "target_samples": "str - Target examples / sample rows.",
                "file_count": "int - Number of source files (optional).",
                "source_information": "str - Source tables info (schema, examples, file paths).",
                "fd_hints": "str - FD or other hints (optional).",
                "hints": "str - Additional hints (optional).",
            },
            output_type="dict - Contains group_by and aggregations plus raw LLM response and prompt.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Operation History: []\\nTarget Table Name: Target1_0\\nTarget Schema: [State: string, AverageTemperature: float]\\nTarget Examples: ...\\nSource Information: Source 0 Name: Source1_0_0 Schema: [dt, AverageTemperature, State, Country]")',
                    "description": "Configure a GROUP_BY/AGGREGATE from an inline case description.",
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
        allowed_operation_list: Optional[List[str]] = None,
        operation_history: Optional[List[str]] = None,
        target_data_name: Optional[str] = None,
        target_data_schema: Optional[str] = None,
        target_samples: Optional[str] = None,
        file_count: Optional[int] = None,
        source_information: Optional[str] = None,
        fd_hints: str = "",
        hints: str = "",
    ) -> Dict[str, Any]:
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
            if operation_history == [] and parsed.get("operation_history_str"):
                try:
                    operation_history = ast.literal_eval(
                        parsed["operation_history_str"]
                    )
                except Exception:
                    pass

        target_data_name = target_data_name or ""
        target_data_schema = target_data_schema or ""
        target_samples = target_samples or ""
        source_information = source_information or ""

        full_prompt = get_group_by_aggregate_prompt(
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples=target_samples,
            file_count=file_count,
            source_information=source_information,
            hints=hints,
            fd_hints=fd_hints,
        )[0]

        response = self.llm_engine(full_prompt)
        response_str = str(response)
        payload = _extract_between_dollars(response_str) or response_str.strip()

        group_by, aggs = _extract_group_by_and_aggs(payload)

        return {
            "group_by": group_by,
            "aggregations": aggs,
            "raw_response": response_str,
            "prompt": full_prompt,
        }


if __name__ == "__main__":
    tool = Configure_GroupBy_Aggregate_Operator_Tool(model_string="gpt-4o-mini")
    print(
        tool.execute(
            query="""
Operation History: []

Target Table Name: Target1_0
Target Schema: ['State': string, 'AverageTemperature': float]
Target Examples: State AverageTemperature\nZhejiang 16.18

Source Information:
Source 0 Name: Source1_0_0
Source 0 Schema: ['dt', 'AverageTemperature', 'AverageTemperatureUncertainty', 'State', 'Country']
""".strip()
        )
    )
