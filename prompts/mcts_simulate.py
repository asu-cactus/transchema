"""
mcts_simulate.py — MCTS Simulation prompt.

Generates a COMPLETE, immediately executable Python script for the schema
transformation.  Unlike get_python_script_simple(), which strictly follows
the operation_history as a fixed sequence, this prompt treats the partial
MCTS plan as GUIDANCE: the LLM reasons about the full pipeline needed and
may add further operations (extra joins, group-bys, projections, type fixes,
etc.) to correctly reach the target schema.

The function signature mirrors get_python_script_simple() so it can be
swapped in at the prompt_type dispatch level.
"""

import sys
from pathlib import Path

_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[1])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)
from hints.hints_static import get_hints_section, PYTHON_SCRIPT_HINT_IDS
from hints.hint import get_hints


def get_mcts_simulate_prompt(
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    hint_source="",
    file_count=0,
    source_data_name_list=None,
    source_data_schema_list=None,
    directory="",
    len_idx_target_idx="",
    raw_target_schema="",
    static_hints=True,
):
    """
    MCTS Simulation prompt.

    Parameters
    ----------
    operation_history : list[str]
        Partial plan from MCTS expansion.  Used as a starting hint, not a
        rigid recipe.  The LLM decides what additional steps are needed.
    target_data_name : str
    target_data_schema : str
    target_samples : str
        Sample rows from the target table (token-budget-capped by the caller).
    source_information_with_location : str
        Formatted block describing all source tables with file paths.
    csv_save_path : str
        Full path where the output CSV must be saved.
    error_string : str
        Execution error(s) from previous code-generation attempts (empty on
        the first trial).

    Returns
    -------
    list[str]  — single-element list containing the prompt string.
    """

    # Compute data-specific v1-text hints (mirrors get_python_script_for_single_step_cot)
    data_specific_hints = ""
    if hint_source and hint_source not in ("none", "") and source_data_name_list is not None:
        schema_for_hints = raw_target_schema if raw_target_schema else target_data_schema
        hint_configs = {
            "get_next_operator": (0, []),
            "join":              (1, [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]),
            "group_by_aggregate": (1, [0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2]),
            "union":             (0, []),
        }
        hint_parts = []
        for pt, (hint_flag, hints_truncate) in hint_configs.items():
            h = get_hints(
                pt, hint_source, schema_for_hints, file_count,
                source_data_name_list, source_data_schema_list, directory, len_idx_target_idx,
                hint_flag, hints_truncate,
            )
            if h and h[0]:
                hint_parts.append(h[0])
        if hint_parts:
            data_specific_hints = "\n".join(hint_parts)

    if operation_history:
        history_section = f"""Partial Operation Plan:
    {operation_history}

Use the operations above as a hint for the first transformation step(s), then reason
about what additional steps are required to produce the correct target schema.
"""
    else:
        history_section = (
            "No prior operations selected. Reason freely about the full pipeline.\n"
        )

    script_hints = get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt="bullet") if static_hints else ""

    prompt = f"""You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should be immediately executable in a correct way, which means it should NOT contain any placeholder for brevity. For example, even if there exist hundreds of source tables, these data need to be loaded completely one by one or in a programmable way.

{history_section}
1. Target Table Name:              {target_data_name}
2. Target Schema:                  {target_data_schema}
3. Target Examples:                {target_samples}
4. Source Information (with paths): {source_information_with_location}
5. Save the result to:             {csv_save_path}

Before writing code, THINK STEP BY STEP about the complete transformation plan:
  a) What does the partial plan above imply for the first operation(s)?
  b) After those operations, what intermediate schema is produced?
  c) What further operations are needed to reach the target schema?
  d) Are there any data-type fixes, string conversions, or column renames required?

Then output your COMPLETE operation plan using this block (one operation per line,
ending with NO_MORE_OPERATION):

$PLAN$
<operation 1>
<operation 2>
...
NO_MORE_OPERATION
$END_PLAN$

Each operation line must use the same format as the operation history above.
Examples of valid operation lines:
  UNION : [test_0, test_1]
  JOIN : [[union_result, test_2]] columns=[[union_result.id, test_2.id]]
  GROUP_BY/AGGREGATE : group_by=[test_0.category] aggregations=[COUNT(test_0.id)]
  NO_MORE_OPERATION

Then generate the Python script that implements the COMPLETE transformation from
raw source tables to the final target CSV.

The code must be immediately executable — no placeholders, no ellipses.  Every source
file must be loaded explicitly.

Keep the code brief: no inline comments, no docstrings, no explanatory print statements.

Please quote the Python script between one single "```Python" and "```".

══════════════════════════════════════════════════════
Hints for Python code generation
══════════════════════════════════════════════════════
{script_hints}
{data_specific_hints}

Errors in previous attempts: {error_string}
"""

    return [prompt]
