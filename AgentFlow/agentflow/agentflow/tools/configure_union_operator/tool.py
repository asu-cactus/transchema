# agentflow/tools/configure_union_operator/tool.py

import ast
import re
from typing import Any, Dict, List, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


TOOL_NAME = "Configure_Union_Operator_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It proposes which tables to UNION based on schema similarity; ambiguous schemas may lead to wrong suggestions.
2) It does not execute UNIONs; it only suggests which tables should be unioned.
3) If operation history is incomplete, it may propose repeated union configurations.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide all source tables (names + schemas) and target schema/examples.
2) Include operation history so the tool avoids repeating unions.
3) Prefer exact schema matches for UNION (no renaming).
"""


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


def get_union_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
):
    prompt = """
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer \"what tables should be Union-ed?\". Take this decision based on \"Operation History\",few shot examples, \"Source\" and \"Target\" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}


- Please answer which tables should be unioned.
- Apply UNION to tables that have exactly the same schema without renaming columns.
- Choose tables having exactly the same schema to union.
- Try not to repeat operation and it's configuration. i.e. Union on tables should only appear once in \"Operation History\".
- You should only answer from available tables of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in format of list where elements are quoted by $. I.e. [$table1$, $table2$, ...].
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
    )
    return [prompt]


def _extract_tables_from_dollar_list(text: str) -> Optional[List[str]]:
    """Extract table names from the [$t1$, $t2$] style output."""
    if not text:
        return None

    # Capture all $...$ occurrences
    tables = [m.strip() for m in re.findall(r"\$([^$]+)\$", text)]
    if tables:
        return tables

    # Fallback: try to parse as a python list literal
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, list):
            return [str(x) for x in obj]
    except Exception:
        pass

    return None


class Configure_Union_Operator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that configures a UNION operator by selecting which tables should be unioned.",
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
            },
            output_type="dict - Contains the union table list plus raw LLM response and prompt.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Operation History: []\\nTarget Table Name: Target1_0\\nTarget Schema: ...\\nTarget Examples: ...\\nSource Information: ...")',
                    "description": "Configure a UNION from an inline case description.",
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

        full_prompt = get_union_prompt(
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples=target_samples,
            file_count=file_count,
            source_information=source_information,
        )[0]

        response = self.llm_engine(full_prompt)
        response_str = str(response)

        tables = _extract_tables_from_dollar_list(response_str)

        return {
            "union_tables": tables,
            "raw_response": response_str,
            "prompt": full_prompt,
        }


if __name__ == "__main__":
    tool = Configure_Union_Operator_Tool(model_string="gpt-4o-mini")
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
