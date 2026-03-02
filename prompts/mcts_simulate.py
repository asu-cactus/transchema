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


def get_mcts_simulate_prompt(
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
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

    if operation_history:
        history_section = f"""Partial Operation Plan (treat this as a STARTING GUIDE, not a fixed sequence):
    {operation_history}

Use the operations above as a hint for the first transformation step(s), then reason
about what additional steps are required to produce the correct target schema.
"""
    else:
        history_section = (
            "No prior operations selected. Reason freely about the full pipeline.\n"
        )

    prompt = f"""You are generating executable Python code at runtime. Your goal is to convert multiple
source tables into the format of the target table.

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
 - Load CSV files using index_col=0 to skip the auto-index first column, e.g.
     source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/lengthY_Z/test_0.csv', index_col=0)
 - Use only the CSV file paths listed in the Source Information section.
 - Ensure every source table contributes to (or is used in) the final output.
 - Apply string or date conversions wherever needed.
 - Note that some column names (e.g., "purpose", "funded_year") may not match the column values
   (e.g., 5, 16844). Treat such columns as aggregation targets (count per purpose, sum for
   funded_year); do NOT use them as Group By columns.
 - The generated table must have exactly the same column names and types as shown in target examples.
 - If two source tables have different columns, do NOT apply UNION.
 - If multiple source tables have exactly the same columns as the target, apply UNION first.
 - If two sources share a few common columns that also appear in the target, apply JOIN first.
 - If m source tables share the same schema with k non-key columns but the target has k×m non-key
   columns (each non-key column renamed per source), JOIN all source tables on the primary key.
 - GROUP BY attributes are never float-typed; they correspond to columns with UNIQUE, non-float values
   in target examples and are usually the leftmost columns in the target schema.
   If a column has float values in target examples, exclude it from GROUP BY.
 - All source tables must appear in the script.  Union tables with the same schema first; then join
   the union result with the other tables on the shared key.  Example: sources D, E, H, I share a
   schema → union them into unioned_df, then join with A, B, C, F, G, J on ROW_WID.
 - If target examples contain duplicate keys or duplicate rows, do NOT apply GROUP BY.
 - If a column has integer values in source but float values in target, apply average aggregation and
   exclude that column from GROUP BY.
 - Each source file has a header; account for it when using concat (union).
 - Do not load source files that are not listed in this prompt.

Hint 1 — Column name vs. value mismatch
  If a column name doesn't reflect its values (e.g., "purpose" holds integers like 5, 10, 15),
  treat the column as an aggregation target (count per purpose), not a GROUP BY column.

Hint 2 — Too many rows in output
  (1) Add GROUP BY on the leftmost non-float unique columns from target examples.
  (2) If GROUP BY is already used, remove some group-by attributes.
  (3) Replace OUTER joins with INNER joins.
  (4) Drop rows that contain NaN values.

Hint 3 — Too few rows in output
  (1) Replace INNER joins with OUTER joins.
  (2) Keep (or add) rows with NaN values.
  (3) Remove GROUP BY, or add more group-by attributes.

Hint 4 — Union vs. wide join
  If m source tables share the same schema with k non-key columns but the target has k×m non-key
  columns (each renamed), JOIN all source tables on the primary key instead of UNION.

Hint 5 — GROUP BY column types
  GROUP BY columns are never float-typed; they are UNIQUE, non-float, usually leftmost in target.

Hint 6 — No GROUP BY for duplicates
  If target examples contain duplicate keys or duplicate rows, skip GROUP BY entirely.

Hint 7 — SUM aggregation signal
  If a column's average value in target is much larger than in source, apply SUM and exclude
  that column from GROUP BY.

Hint 8 — Aggregation on year-like columns
  If a year-like column has abnormal values in target (e.g., 0 or >3000), apply aggregation
  and exclude it from GROUP BY.

Hint 9 — Dimension / aspect join pattern
  JOIN is typically applied on a shared primary key or a foreign-key reference.
  If many sources have different schemas, identify the "dimension table" (most attributes) and
  join the "aspect tables" to it on their shared attribute.
  Example: test_5 (large dimension) joins test_0 on Origen, test_1 on Pronostico, etc.

Hint 10 — Cross-name joins
  Tables may join on columns with different names but similar values.
  Example: test_0.Code ∈ {{AUS, AUT, BEL}} ↔ test_1.Country ∈ {{FRA, BEL, GRA}};
           join on test_0.Code = test_1.Country.

Hint 11 — All sources must be used
  Every source table must appear in the script.  Union same-schema tables, then join with others.

Hint 12 — No GROUP BY for single-column or key-less targets
  Skip GROUP BY if the target has only one column or no identifiable primary key.

Hint 13 — Never group by ALL target columns
  Using every target column as a GROUP BY attribute is always wrong.

Hint 14 — Constant-value columns
  If target examples show constant values in certain columns, reproduce those constants in code.

Hint 15 — String format normalization
  Apply string functions to columns that look similar but differ in format between source and target
  (e.g., "United States" vs. "US", "2023-01-01" vs. "Jan 2023").

Hint 16 — Column type and name fidelity
  Ensure the generated DataFrame has exactly the same column types and names as the target examples.

Hint 17 — index_col=0 for all source reads
  Most source files have a numerical auto-index as the first column; always pass index_col=0 when
  loading them with pd.read_csv().

Errors in previous attempts: {error_string}
"""

    return [prompt]
