"""
mcts_expand.py — MCTS Expansion prompt.


Combines operator selection AND configuration into a single LLM call.
Returns up to k ranked candidate next operators, each with its full configuration,
so no separate "configure" call is needed.

Output format parsed by get_mcts_candidates() in auto_suggest_llm_util.py:

    $CANDIDATE 1$
    OPERATOR: JOIN
    TABLES: [[test_0, test_1]]
    COLUMNS: [[test_0.order_id, test_1.id]]
    $END$

    $CANDIDATE 2$
    OPERATOR: GROUP_BY/AGGREGATE
    GROUP_BY: [test_0.category]
    AGGREGATIONS: [COUNT(test_0.id), SUM(test_0.amount)]
    $END$

    $CANDIDATE 3$
    OPERATOR: NO_MORE_OPERATION
    $END$
"""

import sys
from pathlib import Path

_TRANSCHEMA_ROOT = str(Path(__file__).resolve().parents[1])
if _TRANSCHEMA_ROOT not in sys.path:
    sys.path.insert(0, _TRANSCHEMA_ROOT)
from hints.hints_static import (
    get_hints_section,
    NEXT_OPERATOR_HINT_IDS,
    JOIN_HINT_IDS,
    GROUPBY_AGG_HINT_IDS,
)
from hints.hint import get_hints


def get_mcts_expand_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    fd_hints,
    k=3,
    hint_source="",
    source_data_name_list=None,
    source_data_schema_list=None,
    directory="",
    len_idx_target_idx="",
    raw_target_schema="",
):
    """
    MCTS Expansion prompt.

    Given the current partial operation history, propose up to k ranked next
    operations, each with its COMPLETE configuration (tables, columns,
    aggregation specs, etc.).  The highest-ranked untried candidate will be
    added as a new child node in the MCTS tree; lower-ranked candidates serve
    as fallbacks if the top choice is already explored.

    Parameters
    ----------
    allowed_operation_list : list[str]
        Operator types the LLM may choose from.
    operation_history : list[str]
        Operators already committed in this MCTS path.
    target_data_name : str
    target_data_schema : str
    target_samples : str
        Sample rows from the target table (token-budget-capped by the caller).
    file_count : int
    source_information : str
        Formatted block describing all source tables (schema + examples).
    fd_hints : str
        Functional-dependency hints (empty string when fd_flag == 0).
    k : int
        Maximum number of candidates to return (default 3).

    Returns
    -------
    list[str]  — single-element list containing the prompt string.
    """

    # Compute data-specific operator selection hints (v1-text table matching)
    operator_data_hints = ""
    if hint_source and hint_source not in ("none", "") and source_data_name_list is not None:
        schema_for_hints = raw_target_schema if raw_target_schema else target_data_schema
        operator_h = get_hints(
            "get_next_operator", hint_source, schema_for_hints, file_count,
            source_data_name_list, source_data_schema_list, directory, len_idx_target_idx,
            0, [],
        )
        if operator_h and operator_h[0]:
            operator_data_hints = "\nData-specific table matching:\n" + operator_h[0]

    prompt = f"""You are generating a data-pipeline to transform multiple source tables to the target table and you need to answer "what operation should be performed next?". Take this decision based on "Operation History", the schema of the source, target tables, and examples in the target table.

Your task: propose up to {k} ALTERNATIVE candidates for the SINGLE NEXT operation step, ranked from most to least promising.

CRITICAL: Each candidate is an INDEPENDENT ALTERNATIVE for the same next step.
They are NOT sequential — candidate 2 does NOT build on candidate 1.
Each candidate must reference ONLY the original source tables (or the last result of
the Operation History), never the output of another candidate.

For EVERY candidate you must specify BOTH the operator type AND its full configuration — no
separate configuration step will be performed.

Allowed Operations: {allowed_operation_list}
Operation History (completed so far): {operation_history}

1. Target Table Name:   {target_data_name}
2. Target Schema:       {target_data_schema}
3. Target Examples:     {target_samples}
4. Source Information:  {source_information}
{fd_hints}

══════════════════════════════════════════════════════
CONFIGURATION RULES — one section per operator type
══════════════════════════════════════════════════════

JOIN — join two tables on shared columns
{get_hints_section(JOIN_HINT_IDS, fmt="bullet")}
  • You should only use columns that actually exist in the source tables.
  Format:
    TABLES: [[table1, table2]]
    COLUMNS: [[table1.col_a, table2.col_b], [table1.col_c, table2.col_d], ...]
    (one pair per join condition; use multiple pairs for composite keys)

UNION — stack tables that have IDENTICAL schemas
  • Only union tables with EXACTLY the same column names; do NOT rename.
  • If tables have different schemas, use JOIN instead of UNION.
  Format:
    TABLES: [table1, table2, table3, ...]

GROUP_BY/AGGREGATE — group rows and apply aggregate functions
{get_hints_section(GROUPBY_AGG_HINT_IDS, fmt="bullet")}
  Format:
    GROUP_BY: [table.col1, table.col2, ...]
    AGGREGATIONS: [COUNT(table.col), SUM(table.col2), AVG(table.col3), ...]

PIVOT / UNPIVOT — no additional configuration needed
  Format: (just the operator line; no TABLES or COLUMNS line)

NO_MORE_OPERATION — the pipeline is complete
  Format: (just the operator line)

══════════════════════════════════════════════════════
SELECTION GUIDANCE (apply these rules when ranking candidates)
══════════════════════════════════════════════════════
{get_hints_section(NEXT_OPERATOR_HINT_IDS, fmt="bullet")}
{operator_data_hints}
- If the operation history already covers all needed transformations → propose NO_MORE_OPERATION.
- Do NOT repeat an operation+configuration already present in the operation history.

══════════════════════════════════════════════════════
OUTPUT FORMAT  (follow exactly)
══════════════════════════════════════════════════════
List up to {k} candidates ranked most-to-least promising using the markers below.
Include ONLY candidates you genuinely believe are viable.

$CANDIDATE 1$
OPERATOR: <OPERATOR_TYPE>
<configuration lines>
$END$

$CANDIDATE 2$
OPERATOR: <OPERATOR_TYPE>
<configuration lines>
$END$

... (up to {k} candidates)

Example (Operation History is empty — three independent alternatives for the FIRST step):

$CANDIDATE 1$
OPERATOR: JOIN
TABLES: [[test_0, test_1]]
COLUMNS: [[test_0.order_id, test_1.order_id]]
$END$

$CANDIDATE 2$
OPERATOR: UNION
TABLES: [test_0, test_1]
$END$

$CANDIDATE 3$
OPERATOR: GROUP_BY/AGGREGATE
GROUP_BY: [test_0.category]
AGGREGATIONS: [COUNT(test_0.id), SUM(test_0.revenue)]
$END$

Note: all three candidates above operate on the SAME original source tables.
Candidate 2 does NOT depend on candidate 1 having been applied first.

Now provide your ranked candidates:"""

    return [prompt]
