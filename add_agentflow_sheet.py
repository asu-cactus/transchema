"""
Script to add "AgentFlow Prompt Designs - Operator" sheet to Prompt Design.xlsx.
Run from transchema/ root:  python3 add_agentflow_sheet.py
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

XLSX_PATH = "Prompt Design.xlsx"
SHEET_NAME = "AF Prompt Designs - Operator"

# ---------------------------------------------------------------------------
# Row data: (AgentFlow Component, Section Type, Current AgentFlow Text,
#            Maps To (Multistep), Match Status)
# ---------------------------------------------------------------------------
ROWS = [
    # ── Planner ANALYZE_QUERY ──────────────────────────────────────────────
    (
        "Planner: ANALYZE_QUERY (operator mode)",
        "Task Description",
        "Analyze the given query to determine necessary skills and tools. "
        "You can ONLY suggest operations and tools that are in the available tools list.",
        "No multistep equivalent (multistep uses hardcoded allowed_operation_list)",
        "No Multistep Equivalent",
    ),
    (
        "Planner: ANALYZE_QUERY (operator mode)",
        "Context fields",
        "Inputs: Query, Available tools, Metadata for tools",
        "No multistep equivalent",
        "No Multistep Equivalent",
    ),
    (
        "Planner: ANALYZE_QUERY (operator mode)",
        "Output format",
        "Summary of query, lists of skills and tools with explanations, additional considerations.",
        "No multistep equivalent",
        "No Multistep Equivalent",
    ),
    # ── Planner GENERATE_NEXT_STEP ─────────────────────────────────────────
    (
        "Planner: GENERATE_NEXT_STEP (operator mode)",
        "Task Description",
        "Task: Determine the optimal next step to build the data transformation pipeline operator by operator. "
        "You are operating at OPERATOR granularity. "
        "CRITICAL CONSTRAINT: You can ONLY use tools from the available tools list.",
        "get_next_operator_prompt — Task: 'what operation should be performed next?' "
        "Allowed Operations listed; Operation History; source/target schema + examples.",
        "Needs Update → Done",
    ),
    (
        "Planner: GENERATE_NEXT_STEP (operator mode)",
        "Tool Descriptions",
        "Configure_Join_Operator_Tool, Configure_Union_Operator_Tool, "
        "Configure_GroupBy_Aggregate_Operator_Tool, Add_Pivot_Tool, Add_Unpivot_Tool, "
        "Code_Gen_And_Score_Tool, Critique_Pipeline_Tool — each with usage guidance.",
        "Allowed Operations list in multistep (JOIN, UNION, GROUP_BY, AGGREGATE, etc.)",
        "Needs Update → Done",
    ),
    (
        "Planner: GENERATE_NEXT_STEP (operator mode)",
        "Domain Hints (NEW — added in this update)",
        "=== DOMAIN HINTS FOR OPERATOR SELECTION ===\n"
        "[get_hints_section(NEXT_OPERATOR_HINT_IDS, fmt='bullet')]\n"
        "Hint IDs: [1,2,3,4,5,6,9,11,16]",
        "get_next_operator_prompt — static_hints block using NEXT_OPERATOR_HINT_IDS",
        "Needs Update → Done",
    ),
    (
        "Planner: GENERATE_NEXT_STEP (operator mode)",
        "Context fields",
        "Query, Query Analysis, Available Tools, Toolbox Metadata, "
        "Previous Steps and Their Results, Current Step, Remaining Steps.",
        "Source Information, Operation History, Target Schema, Target Examples",
        "Needs Update → Done",
    ),
    (
        "Planner: GENERATE_NEXT_STEP (operator mode)",
        "Response format",
        "Justification → Context → Sub-Goal → Tool Name (in that order, nothing after).",
        "Final answer in $OPERATOR$ quotes",
        "Needs Update → Done",
    ),
    # ── Configure_Join_Operator_Tool ───────────────────────────────────────
    (
        "Configure_Join_Operator_Tool",
        "Task Description",
        "You are generating a data-pipeline to transform multiple source tables to target table "
        "and you need to answer 'what tables should be joined and at which columns?'",
        "get_join_prompt — identical task description",
        "Identical",
    ),
    (
        "Configure_Join_Operator_Tool",
        "Case Info format",
        "transformation_case_info (contains target table name, schema, examples, "
        "multi source information, operation history)",
        "Separate args: target_data_name, target_data_schema, target_samples, "
        "source_information, operation_history, hints, fd_hints",
        "Needs Update → Done",
    ),
    (
        "Configure_Join_Operator_Tool",
        "Task+Case Specific Hints",
        "[get_hints_section(JOIN_HINT_IDS, fmt='bullet')]\nHint IDs: [7,8,9]",
        "get_join_prompt — get_hints_section(JOIN_HINT_IDS, fmt='bullet')",
        "Needs Update → Done",
    ),
    (
        "Configure_Join_Operator_Tool",
        "Return format",
        "[ [table1, table2], [table1.col1, table2.col1], ... ] within $ quotes",
        "Same format",
        "Identical",
    ),
    # ── Configure_Union_Operator_Tool ──────────────────────────────────────
    (
        "Configure_Union_Operator_Tool",
        "Task Description",
        "You are generating a data-pipeline to transform multiple source tables to target table "
        "and you need to answer 'what tables should be Union-ed?'. Take this decision based on "
        "'Operation History', few shot examples, 'Source' and 'Target' (table schema as well as "
        "the examples) information provided below.",
        "get_union_prompt — identical task description (now aligned)",
        "Needs Update → Done",
    ),
    (
        "Configure_Union_Operator_Tool",
        "Case Info format",
        "transformation_case_info",
        "Separate args: target_data_name, target_data_schema, target_samples, "
        "source_information, operation_history",
        "Needs Update → Done",
    ),
    (
        "Configure_Union_Operator_Tool",
        "Task Specific General Hints",
        "No domain hints (none in mapping for Union)",
        "No domain hints in get_union_prompt either",
        "Identical",
    ),
    (
        "Configure_Union_Operator_Tool",
        "Return format",
        "[$table1$, $table2$, ...]",
        "Same format",
        "Identical",
    ),
    # ── Configure_GroupBy_Aggregate_Operator_Tool ──────────────────────────
    (
        "Configure_GroupBy_Aggregate_Operator_Tool",
        "Task Description",
        "You are generating a data-pipeline to transform multiple source tables to target table "
        "and you need to answer: 1. Which columns for Group By? 2. Which columns Aggregated? "
        "3. Which Aggregation functions?",
        "get_group_by_aggregate_prompt — identical task description",
        "Identical",
    ),
    (
        "Configure_GroupBy_Aggregate_Operator_Tool",
        "Case Info format",
        "transformation_case_info",
        "Separate args: target_data_name, target_data_schema, target_samples, "
        "source_information, operation_history, hints, fd_hints",
        "Needs Update → Done",
    ),
    (
        "Configure_GroupBy_Aggregate_Operator_Tool",
        "Task+Case Specific Hints",
        "[get_hints_section(GROUPBY_AGG_HINT_IDS, fmt='bullet')]\nHint IDs: [10,14,16,17,18,20,21]",
        "get_group_by_aggregate_prompt — get_hints_section(GROUPBY_AGG_HINT_IDS, fmt='bullet')",
        "Needs Update → Done",
    ),
    (
        "Configure_GroupBy_Aggregate_Operator_Tool",
        "Return format",
        '"group_by" = [...], "aggregations" = [agg_func(col), ...]',
        "Same format",
        "Identical",
    ),
    # ── Code_Gen_And_Score_Tool ────────────────────────────────────────────
    (
        "Code_Gen_And_Score_Tool",
        "Task Description",
        "You are generating executable Python code at runtime. Please generate a Python script "
        "to convert multiple source tables to the format of the target table and STRICTLY follow "
        "the sequence of the operations mentioned in the action history below.",
        "get_python_script_simple — identical task description",
        "Identical",
    ),
    (
        "Code_Gen_And_Score_Tool",
        "Context format",
        "Transformation Context: {query}\nAction History (follow this sequence): {memory_actions}",
        "Operation History: {operation_history}\nSource Information: {source_information_with_location}",
        "Needs Update → Done",
    ),
    (
        "Code_Gen_And_Score_Tool",
        "Task+Case Specific Hints",
        "[get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt='bullet')]\n"
        "Hint IDs: [1,2,3,4,5,10,11,16,17,24,27,28,29,30,31,32]",
        "get_python_script_simple — get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt='bullet')",
        "Needs Update → Done",
    ),
    (
        "Code_Gen_And_Score_Tool",
        "Return format",
        "```Python ... ``` + error string: Errors in previous attempts: {error_string}",
        "Same format",
        "Identical",
    ),
    # ── Critique_Pipeline_Tool ─────────────────────────────────────────────
    (
        "Critique_Pipeline_Tool",
        "Task Description",
        "You are critiquing a data-pipeline that transforms multiple source tables to follow the "
        "schema of the target table. Review the current pipeline and suggest corrections.",
        "critique.py query_generator — similar task description",
        "Needs Update → Done",
    ),
    (
        "Critique_Pipeline_Tool",
        "Case Info format",
        "transformation_case_info (target table, sources, operation history)",
        "critique.py — query contains target schema, examples, source info, operation history",
        "Needs Update → Done",
    ),
    (
        "Critique_Pipeline_Tool",
        "Per-operator config instructions",
        "--For Join: tables + join attributes.\n"
        "--For Union: tables to union.\n"
        "--For GroupBy: Group By attributes (leftmost non-float unique cols).\n"
        "--For Aggregate: aggregation function + column (not in GroupBy).",
        "critique.py — similar per-operator guidance in query_generator",
        "Needs Update → Done",
    ),
    (
        "Critique_Pipeline_Tool",
        "Task+Case Specific Hints",
        "[get_hints_section(CRITIQUE_HINT_IDS, fmt='numbered')]\n"
        "Hint IDs: [4,5,7,8,9,10,11,12,13,15,16,18,19,22,23,24,25,26,28]",
        "critique.py — get_hints_section(CRITIQUE_HINT_IDS, fmt='numbered')",
        "Needs Update → Done",
    ),
    (
        "Critique_Pipeline_Tool",
        "Return format",
        "$CRITIQUE: <detailed critique and corrected pipeline>$",
        "critique.py — similar $CRITIQUE: ...$ delimited format",
        "Needs Update → Done",
    ),
    # ── Verifier.verificate_context ────────────────────────────────────────
    (
        "Verifier: verificate_context (operator mode)",
        "Task Description",
        "Task: Evaluate whether the operator-driven transformation pipeline has produced a correct "
        "and complete result, or whether more steps are needed.",
        "No multistep equivalent",
        "No Multistep Equivalent",
    ),
    (
        "Verifier: verificate_context (operator mode)",
        "Context fields",
        "Query, Available Tools, Toolbox Metadata, Initial Analysis, "
        "Memory (Tools Used & Results)",
        "No multistep equivalent",
        "No Multistep Equivalent",
    ),
    (
        "Verifier: verificate_context (operator mode)",
        "Stop/Continue logic",
        "1. Review operator configs in memory.\n"
        "2. Identify whether all operators configured to produce target schema.\n"
        "3. Code and Score Check: if Code_Gen_And_Score_Tool result with score=1.0 and "
        "no missed items → STOP; else CONTINUE.\n"
        "Response: 2-3 sentences ending with 'Conclusion: STOP' or 'Conclusion: CONTINUE'.",
        "No multistep equivalent",
        "No Multistep Equivalent",
    ),
]

# ---------------------------------------------------------------------------
# Match status fill colors
# ---------------------------------------------------------------------------
FILL_COLORS = {
    "Identical": "C6EFCE",              # green
    "Needs Update → Done": "FFEB9C",    # yellow
    "No Multistep Equivalent": "BDD7EE",  # blue
    "No AgentFlow Equivalent": "FCE4D6",  # orange
}

HEADER_FILL = "4472C4"  # dark blue
HEADER_FONT_COLOR = "FFFFFF"


def build_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet(title=SHEET_NAME)

    headers = [
        "AgentFlow Component",
        "Section Type",
        "Current AgentFlow Text",
        "Maps To (Multistep)",
        "Match Status",
    ]

    # Write header row
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True, color=HEADER_FONT_COLOR)
        cell.fill = PatternFill("solid", fgColor=HEADER_FILL)
        cell.alignment = Alignment(wrap_text=True, vertical="top")

    # Write data rows
    for row_idx, row_data in enumerate(ROWS, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(wrap_text=True, vertical="top")

        # Color the Match Status cell (column 5)
        status = row_data[4]
        if status in FILL_COLORS:
            ws.cell(row=row_idx, column=5).fill = PatternFill(
                "solid", fgColor=FILL_COLORS[status]
            )

    # Set column widths
    col_widths = [36, 32, 70, 60, 26]
    for col_idx, width in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Freeze header row
    ws.freeze_panes = "A2"


def main():
    wb = openpyxl.load_workbook(XLSX_PATH)
    if SHEET_NAME in wb.sheetnames:
        del wb[SHEET_NAME]
    build_sheet(wb)
    wb.save(XLSX_PATH)
    print(f"Sheet '{SHEET_NAME}' added to {XLSX_PATH} ({len(ROWS)} rows).")


if __name__ == "__main__":
    main()
