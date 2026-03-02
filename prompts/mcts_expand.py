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

    prompt = f"""You are building a data-pipeline to transform multiple source tables into the target table.

Your task: given the current "Operation History", propose up to {k} ALTERNATIVE candidates for
the SINGLE NEXT operation step, ranked from most to least promising.

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
  • Tables typically join on a shared primary/foreign key.
  • Columns may have DIFFERENT NAMES but similar values
    (e.g., test_0.Code = test_1.Country; test_0.Country = test_2.Host).
  • If many sources have different schemas, identify a "dimension table"
    (the one with the most attributes) and join the "aspect tables" to it
    on their shared columns.
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
  • Group-by columns are NEVER float-typed.
  • Group-by columns have UNIQUE integer or string values in target examples
    and are usually the LEFTMOST columns of the target schema.
  • Exclude any column that has float values in target examples from group-by.
  • If target examples show duplicate keys or duplicate rows, do NOT use GROUP_BY.
  • Choose aggregate functions by inspecting value ranges:
      – COUNT for many similar small integers in target
      – SUM if target values are much larger than source values
      – AVG if source has integer values but target has float values for that column
      – COUNT DISTINCT if many similar but slightly different integer values
  • A group-by column MUST NOT also be an aggregation column.
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
- If any two source tables have DIFFERENT columns → do NOT propose UNION.
- If multiple source tables have EXACTLY the same column names as each other AND as the target
  → propose UNION first (highest priority).
- If two sources share a few common columns that also appear in the target
  → propose JOIN first.
- If m source tables share the same schema with k non-key columns but the target has k×m non-key
  columns (each non-key column is renamed per source) → propose JOIN on the primary key.
- If target examples contain duplicate keys or duplicate rows → do NOT propose GROUP_BY/AGGREGATE.
- NEVER include ALL target columns as group-by columns.
- ALL source tables must be included somewhere in the pipeline.
- If the operation history already covers all needed transformations → propose NO_MORE_OPERATION.
- Do NOT repeat an operation+configuration already present in the operation history.
- Confirm that ALL columns in the target schema are accounted for by the proposed operations.
- Note: some column names (e.g., "purpose", "funded_year") may not reflect the actual column values
  (e.g., integers 5 or 16844). In such cases, treat the column as an aggregation target (count, sum),
  not a group-by column.
- All source tables have to be used. For example, if source schemas include D, E, H, I with the same
  schema, union them first, then join the result with the remaining tables on the shared key.

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
