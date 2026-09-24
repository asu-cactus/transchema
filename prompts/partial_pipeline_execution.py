"""
partial_pipeline_execution.py — Strict partial-pipeline execution prompt.

Unlike get_mcts_simulate_prompt() (which treats operation_history as guidance
and lets the LLM extend it toward the target) and get_python_script_simple()
(which asks the LLM to "STRICTLY follow the sequence" while also handing it
the target schema/samples — contradictory once operation_history is a
partial, non-final prefix), this prompt has exactly one job: apply the given
operations, in order, and nothing else. No target information is provided,
so there is nothing to "reach" or optimize toward.

Used to materialize the real intermediate schema at a given MCTS search node
(the operations already committed to in rollout_history) so JOIN candidates
can be ranked against it, without letting the LLM silently complete the plan.
"""


def get_partial_pipeline_execution_prompt(
    operation_history,
    source_information_with_location,
    csv_save_path,
    error_string="",
):
    prompt = f"""
You are generating executable Python code at runtime.

Your ONLY job is to apply the EXACT sequence of operations listed below to the
source tables, in the exact order given — nothing more, nothing less. Do NOT
add, remove, reorder, skip, or infer any additional operation beyond what is
explicitly listed. Do NOT try to reach any particular final schema or format.
This is a PARTIAL, intentionally incomplete pipeline — the result of applying
just these operations is exactly what is wanted, even if it does not look
"finished."

Operations to apply, strictly in this order:
{operation_history}

Operator format reference:
- "JOIN : [[t1, t2]] columns=[[t1.c1, t2.c2]]" -> merge t1 and t2 on the given
  columns (inner join unless the string says otherwise).
- "UNION : [t1, t2, ...]" -> concatenate the listed tables.
- "GROUP_BY : [col1, col2, ...]" -> group by the listed columns (do not
  aggregate unless an AGGREGATE step is also listed).
- "AGGREGATE : [SUM(col), COUNT(col), ...]" -> apply the listed aggregations
  to the current grouping.
- "GROUP_BY/AGGREGATE : ..." -> combined step, apply both together.
- "PIVOT" / "UNPIVOT" -> these carry no explicit configuration here, so choose
  a reasonable configuration based on the SOURCE data's structure ALONE — do
  NOT use any notion of a target schema to decide this, since none is given.
- "COLUMN_TRANSFORM : [out_a = <expr>, out_b = <expr>, ...]" -> build each listed
  output column by evaluating its expression row by row. This does NOT collapse
  rows; the row count stays the same. The entries ARE the output schema: emit
  them in the order listed and drop any column not listed.
  Each <expr> is one of:
    t.c                              copy the column through (renamed to the name
                                     on the left of "=")
    0  /  'NA'                       a bare literal makes a constant column
    SUM|AVG|MAX|MIN(t.c1, t.c2, ...) combine the listed columns ROW BY ROW into one
                                     column -- NOT a group-wise aggregation
    MAX(...) - MIN(...)              two functions combined arithmetically
    COALESCE(t.c, 0)                 treat nulls as zero
    FORMAT(t.dt, 'pattern')          re-render a date/time using the given
                                     strftime-style pattern
    EXTRACT(MONTH FROM t.dt)         pull YEAR, MONTH, DAY, HOUR, MINUTE or DOW
                                     out into a new column
    UPPER|LOWER|TRIM|LENGTH(t.c)
    CONCAT(t.c1, '-', t.c2)          join the parts into one string
    SUBSTR(t.c, start, len)
    SPLIT(t.c, 'sep', index)         split on the separator, keep the 0-based index
    REPLACE(t.c, 'old', 'new')
    CAST(t.c AS int|float|str)
  Functions may be nested, e.g. UPPER(TRIM(t.city)).
  A legacy step may name this operator COLUMN_AGGREGATION, FORMAT_DATETIME or
  PROJECT, and PROJECT-style entries may be written "t.c1 -> out_a" instead of
  "out_a = t.c1"; treat all of these exactly as COLUMN_TRANSFORM above.

Source Information: {source_information_with_location}

These file paths listed above are the ONLY valid paths to READ data from. If
an operation refers to the same table more than once (e.g. a self-join),
load that SAME source file path multiple times — do not substitute any other
path, and never invent a new one.

Write the result of applying exactly the operations above — and nothing more
— to this path: {csv_save_path}

IMPORTANT: that save path is OUTPUT ONLY. It does not exist before this
script runs and must never be read from, imported, or treated as a source —
not even when the same table needs to be loaded more than once. All reads
must come from the Source Information paths above.

The script must be complete and immediately executable: load all needed
source files explicitly (no placeholders), apply exactly the listed
operations in order, then save the result. Do not perform any operation not
listed above. Do not attempt to match a target table's shape.

Please quote the Python script between one single "```Python" and "```".

Errors in previous attempts: {error_string}
"""
    return [prompt]
