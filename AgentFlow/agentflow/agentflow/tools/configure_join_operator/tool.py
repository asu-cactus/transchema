# agentflow/tools/configure_join_operator/tool.py

import ast
import re
from typing import Any, Dict, List, Optional

from agentflow.engine.factory import create_llm_engine
from agentflow.tools.base import BaseTool


# Tool name mapping - this defines the external name for this tool
TOOL_NAME = "Configure_Join_Operator_Tool"


LIMITATION = f"""
The {TOOL_NAME} has several limitations:
1) It proposes join inputs/keys based on schemas/examples and may be ambiguous if keys are not evident.
2) It does not execute joins; it only suggests which tables/columns to join.
3) If intermediate results are missing or schemas are incomplete, join suggestions may be low-confidence.
"""


BEST_PRACTICE = f"""
For optimal results with the {TOOL_NAME}:
1) Provide full source table schemas and representative examples.
2) Provide the target schema and target examples so the join can be aligned to target columns.
3) Include operation history to avoid repeating prior join configurations.
4) Provide FD hints / join key hints when available.
"""


def _extract_between_dollars(text: str) -> Optional[str]:
    if not text:
        return None
    m = re.search(r"\$(.*?)\$", text, flags=re.DOTALL)
    if not m:
        return None
    return m.group(1).strip()


def _safe_literal_eval_list(text: str) -> Optional[Any]:
    """Best-effort parse of a Python-like literal list."""
    if not text:
        return None
    try:
        return ast.literal_eval(text)
    except Exception:
        return None


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


def get_join_prompt(
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
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer \"what tables should be joined and at which columns?\". Take this decision based on \"Operation History\", \"Source\" and \"Target\" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.


1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}


-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}


- Please answer which tables should be joined and at which columns that hasn't appeared yet in \"operation history\".
- Usually tables will be joined on shared columns. In some popular cases, the shared column(s) is/are the primary key of each table to be joined. In some other popular cases, the shared column(s) is/are the primary key of one table to be joined and the foreign key of the other table to be joined.
- If many source tables have different schemas (columns), look for a dimension table that has a lot of attributes and join it with each of the rest tables (aspect tables) on shared attributes. For example, test_5.csv has columns: ,Fecha,Mes,IdAhogado,IdPersona,Localidad,Provincia,CCAA,Hora,Latitud_inc,Longitud_inc,Sexo,Edad,Nacionalidad,Origen,Extraccion,Causa,TipoAhogamiento,Factor,Intervencion,Pronostico,Localizacion,Riesgo,Reanimacion,Vigilancia,Actividad,Deteccion,ID,Estacion,Estado,Latitud_est,Longitud_est,T_med,T_max,T_min,Precipitaciones,Presion,Dir. vi.,V_Viento,Nubosidad,ProfNievecm,InsolacHoras,Distancia, test_0.csv has columns ,IdOrigen,Origen, it means test_5 may join with test_0 on Origen. Then, test_1.csv has columns ,IdPronostico,Pronostico,Mortal, so test_5 will also join with test_1 on Pronostico. Similarly, test_5 will join with test_2 (IdDeteccion,Deteccion) on Deteccion, join with test_3 (IdTipo,TipoAhogamiento) on TipoAhogamiento, join with test_4 (IdInterv,Intervencion) on Intervencion, join with test_6 (IdActividad,Actividad) on Actividad, join with test_7 (IdCausa,Causa) on Causa, and join with test_8 (IdReanima,Reanimacion) on Reanimacion.
- Two different tables may join on shared columns that have different names. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host.
- You should only answer from available columns of the source tables.
- Only return two tables that should be joined and on which columns.
- Choose tables that contain columns similar to columns in the target tables to be joined.
- The final answer should be in format of list.
- The first element of list should be the list of two tables that should be joined.
- The next elements should be list of two columns on which the join should be perfomed.
- i.e. [ [table1, table2], [table1.join_column1,table2.join_column1], [table1.join_column2,table2.join_column2],...]
- The final answer list should be within $ quotes strictly. [i.e. $ Final Answer List $]
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


class Configure_Join_Operator_Tool(BaseTool):
    require_llm_engine = True

    def __init__(self, model_string: str = "gpt-4o-mini"):
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description="A tool that configures a JOIN operator by selecting which two tables to join and the join columns.",
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
            output_type="dict - Contains the join configuration as a parsed list when possible, plus raw LLM response and prompt.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Operation History: []\nTarget Table Name: Target1_0\nTarget Schema: [State: string, AverageTemperature: float]\nTarget Examples: ...\nSource Information: Source 0 Name: Source1_0_0 Schema: [dt, AverageTemperature, State, Country]")',
                    "description": "Configure a JOIN from an inline case description.",
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

        full_prompt = get_join_prompt(
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
        join_list = _safe_literal_eval_list(payload)

        return {
            "join_spec": join_list if join_list is not None else payload,
            "raw_response": response_str,
            "prompt": full_prompt,
        }


if __name__ == "__main__":
    tool = Configure_Join_Operator_Tool(model_string="gpt-4o-mini")
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
