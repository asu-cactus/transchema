"""
Central repository of all static hint texts used across prompt templates.

Each hint is indexed by its canonical number (1–32) from the hint reference table.
Use ``get_hints_section`` to build a formatted hints block for any prompt.

Hint-to-prompt mapping (from Current Prompt Mapping):
  GetNextOperator        : [1, 2, 3, 4, 5, 6, 9, 11, 16]
  ConfigureJoin          : [7, 8, 9]
  ConfigureGroupByAgg    : [10, 14, 16, 17, 18, 20, 21]
  GetPythonScript        : [1, 2, 3, 4, 5, 10, 11, 16, 17, 24, 27, 28, 29, 30, 31, 32]
  Critique               : [4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 22, 23, 24, 25, 26, 28]
"""

# ---------------------------------------------------------------------------
# Canonical hint texts
# ---------------------------------------------------------------------------

HINTS = {
    # --- Operation Selection ---
    1: (
        "If any two source tables have different columns, DO NOT give the UNION operation."
    ),
    2: (
        "If there are multiple source tables and the target table having exactly same "
        "columns, give Union operation first priority."
    ),
    3: (
        "If there are two source tables with different schemas that share one or a few "
        "common columns, which exist in the target data, give Join operation first priority."
    ),
    4: (
        "If multiple source tables share the same schema while the target table "
        "(i.e., target examples) also share the same schema, UNION must be used. "
        "However if m source tables share the same schema consisting of k non-key columns, "
        "but the target table has renamed each non-key column shared into k different "
        "columns, and thus consists of k × m non-key columns, JOIN should be applied to "
        "join all source tables on the primary key."
    ),
    5: (
        "All source tables have to be used in all cases. For example, given target examples "
        "with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, "
        "B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, "
        "D/E/H/I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,"
        "MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, "
        "G<ROW_WID,COLLECTION_EVENTS_NUM>, J<ROW_WID,VISITS_NUM> — all tables with same "
        "schema (D,E,H,I) must be unioned, then joined with A,B,C,F,G,J on ROW_WID. "
        "Projection applied last. Similarly for multi-attribute targets with "
        "dimension+aspect table patterns."
    ),
    6: (
        "Please try to make sure, using the operator history, that ALL THE COLUMNS IN "
        "THE TARGET TABLE ARE ACCOUNTED FOR."
    ),

    # --- Join Config ---
    7: (
        "Usually tables will be joined on shared columns. In some popular cases, the "
        "shared column(s) is/are the primary key of each table to be joined. In some "
        "other popular cases, the shared column(s) is/are the primary key of one table "
        "and the foreign key of the other table."
    ),
    8: (
        "If many source tables have different schemas (columns), look for a dimension "
        "table that has a lot of attributes and join it with each of the rest tables "
        "(aspect tables) on shared attributes. For example, test_5.csv has many columns "
        "(Fecha, Mes, IdAhogado, ..., Distancia); test_0.csv has (IdOrigen, Origen) — so "
        "test_5 joins with test_0 on Origen. Then test_1.csv (IdPronostico, Pronostico, "
        "Mortal) joins on Pronostico. Similarly test_5 joins with test_2 on Deteccion, "
        "test_3 on TipoAhogamiento, test_4 on Intervencion, test_6 on Actividad, test_7 "
        "on Causa, test_8 on Reanimacion."
    ),
    9: (
        "Two different tables may join on shared columns that have different names. "
        "For example, test_0 has a Code column with values AUS, AUT, BEL, CAN, FRA, "
        "while test_1 has a Country column with values FRA, BEL, GRA, USA, CAN — these "
        "can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has Country "
        "(Afghanistan, Albania,...) and test_2 has Host (France, Switzerland,...), they "
        "could join on Country=Host. Furthermore, test_2.HostCity can join with test_3.City "
        "if both contain city names."
    ),

    # --- GroupBy Rules ---
    10: (
        "GROUP BY attribute(s) is(are) never of float types and it(they) often "
        "correspond(s) to the column(s) that has (have) all distinct/unique values in the "
        "target examples. These columns are usually at the leftmost part of the target "
        "schema. If you found a column in the target examples contain float values, do not "
        "include the column as GROUP BY attribute."
    ),
    11: (
        "If duplicate tuples or duplicate keys exist in the target examples, no GROUP BY "
        "should be used."
    ),
    12: (
        "No GROUP BY operator should be applied if the target examples have a single "
        "column or there is no primary key in the target examples."
    ),
    13: (
        "IMPORTANT: NEVER use all target columns as the GROUP BY columns!!!"
    ),
    14: (
        "If a column is part of a group by operation, it will NOT be part of an "
        "aggregation operation."
    ),
    15: (
        "If the output data from the last generated python script has the same schema "
        "with the target examples, however the key constraints that exist in the target "
        "examples do not exist in the generated output data, please add a GroupBy. The "
        "GroupBy attributes must be the primary key of the target examples (i.e., "
        "attributes serving as unique tuple identifier)."
    ),

    # --- Aggregation ---
    16: (
        "Note that some column names, e.g., purpose, funded_year, may not match the "
        "values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case "
        "consider the column to be aggregation, e.g., count per purpose, and sum for "
        "funded_year. They should not be used in Group By columns."
    ),
    17: (
        "If a column has integer values in one of the source tables, but the same column "
        "has float values in the target tables (e.g., user_id or age has float values "
        "1211.22 or 33.17 in target but integer values 1001 or 35 in source), an average "
        "aggregation should be applied to the column and the column should NOT be "
        "considered as GROUP BY attribute."
    ),
    18: (
        "If a column that usually has value range (such as year or funded_year) in the "
        "target table has abnormal values (e.g., 0 or 16888 or >3000 for year), an "
        "aggregation should be applied to the column and this column MUST be EXCLUDED "
        "from the Group By columns."
    ),
    19: (
        "If the average value of a column in the target examples is significantly bigger "
        "than its average values in the source tables, sum aggregation should be applied "
        "to the column, and this column should be excluded from the Group By columns."
    ),
    20: (
        "If many columns in the target table have similar integer values, it probably "
        "suggests a count aggregation should be used."
    ),
    21: (
        "If in the target data examples, many columns have similar but different numerical "
        "values such as 5 5 4 5 4 in each row, it indicates that a COUNT DISTINCT is used."
    ),
    22: (
        "For ANY average/mean aggregation, you MUST use the plain, unweighted "
        "mean (.mean() or AGG('mean')) — this is not optional. It is STRICTLY "
        "FORBIDDEN to approximate the average as (min + max) / 2, or to compute "
        "a weighted average by multiplying the value column by any other column "
        "(a count, total, or size column) and dividing by that column's sum — "
        "e.g. sum(value * weight) / sum(weight) or "
        "(df['Median'] * df['Total']).sum() / df['Total'].sum() are BOTH WRONG, "
        "even if a plausible weighting column (like 'Total' or 'Count') exists "
        "in the source data. Using any of these approximations instead of the "
        "simple mean WILL produce an incorrect result, no matter how close the "
        "numbers look."
    ),

    # --- Row Debugging ---
    23: (
        "If the resulting data generated by the failed Python script has the same schema "
        "with the target examples, but has more rows, it may indicate: (1) A Group By and "
        "Aggregate are missing — add GroupBy using leftmost non-float unique attributes and "
        "choose aggregation based on value ranges. (2) If GroupBy already used, remove some "
        "GroupBy attributes. (3) If OUTER join used, replace with INNER join. (4) Remove "
        "rows containing NaN values."
    ),
    24: (
        "If the resulting data generated by the failed Python script has the same schema "
        "with the target examples, but has fewer rows, it may indicate: (1) If INNER join "
        "used, replace with OUTER join. (2) Keep rows containing NaN values. (3) If Group "
        "By is used, remove it or use more Group By attributes."
    ),

    # --- Data Format ---
    25: (
        "Please look at the target examples, and ensure the generated data has the same "
        "type and name for each column in the target examples."
    ),
    26: (
        "Consider applying string functions to certain columns that look similar but have "
        "different formats in the target and resulting data examples."
    ),
    27: (
        "If in the target data examples, many columns have constant values, use the same "
        "constant value in the Python script for those columns."
    ),
    28: (
        "You may use string conversions or date conversions if needed."
    ),

    # --- CSV Handling ---
    29: (
        "Most source files have a numerical index column, which is always the first column, "
        "and it should be ignored in the transformation. Therefore, when reading a CSV file, "
        "please add index_col=0."
    ),
    30: (
        "Note that each source file has a header. The first line of the csv file is a "
        "header, which should be considered before performing queries such as concat (union)."
    ),
    31: (
        "Your code should only take the CSV file paths given in the Source Data Information "
        "as inputs."
    ),
    32: (
        "Please do not use source files that are not mentioned in this prompt."
    ),

    # --- Code Quality ---
    33: (
        "Please ensure all operation output contributed (or used) by the final output."
    ),
    34: (
        "NEVER hardcode specific data values from the target examples or source data "
        "into the Python script (e.g., do NOT write a fixed list of category names, "
        "IDs, or filter values observed in the samples). The training data shown may "
        "not match the full test data, so hardcoded filters will silently drop rows "
        "or produce wrong results. Always derive values dynamically from the source "
        "tables."
    ),
    35: (
        "If a JOIN produces missing/NaN values for unmatched rows, do NOT fill them "
        "with an arbitrary placeholder constant (e.g., fillna(1), fillna('unknown')). "
        "Leave them as NaN/empty. If you must fill a missing value, use 0 — never "
        "invent some other constant."
    ),
    36: (
        "NEVER join using left_index=True/right_index=True. If a named key/ID "
        "column exists, join on it directly by name (on=, left_on=/right_on=)."
    ),
}

# ---------------------------------------------------------------------------
# Per-prompt hint ID lists (from Current Prompt Mapping)
# ---------------------------------------------------------------------------

NEXT_OPERATOR_HINT_IDS = [1, 2, 3, 4, 5, 6, 9, 11, 16]
JOIN_HINT_IDS = [7, 8, 9, 35, 36]
GROUPBY_AGG_HINT_IDS = [10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22]
GROUPBY_HINT_IDS = [10, 11, 12, 13, 14]          # group-by column selection only
AGGREGATE_HINT_IDS = [14, 16, 17, 18, 19, 20, 21, 22]  # aggregation function selection only
PYTHON_SCRIPT_HINT_IDS = [1, 2, 3, 4, 5, 10, 11, 16, 17, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
CRITIQUE_HINT_IDS = [4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 34, 35, 36]
# Pipeline-level: combined design + code generation (single_step_cot / Create_New_Pipeline)
PIPELINE_HINT_IDS = [
    1, 2, 3, 4, 5, 6,          # Operator selection (UNION vs JOIN, all tables used)
    7, 8, 9, 35, 36,             # Join config (PK/FK, dimension tables, different-name joins, no fillna padding, no left_index/right_index)
    10, 11, 12, 13,             # GroupBy rules (no float keys, no duplicate keys, never all cols)
    16, 17, 18, 19, 20, 21, 22, # Aggregation patterns (incl. always use mean, not min+max/2)
    25, 26, 27, 28,             # Data format (type/name match, string conv, constants)
    29, 30, 31, 32, 33,         # CSV handling (index_col=0, header, paths, all outputs used)
    34,                         # Never hardcode values from training samples
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_hints_section(hint_ids, fmt="numbered"):
    """Return a formatted hints block for the given hint IDs.

    Parameters
    ----------
    hint_ids : list[int]
        Ordered list of hint numbers to include.
    fmt : str
        ``"numbered"``  → each hint rendered as ``Hint N:\\n<text>``
        ``"bullet"``    → each hint rendered as ``- <text>``

    Returns
    -------
    str
        Ready-to-embed hints string.
    """
    lines = []
    for i, hint_id in enumerate(hint_ids, start=1):
        text = HINTS[hint_id]
        if fmt == "numbered":
            lines.append(f"Hint {i}:\n{text}")
        else:
            lines.append(f"- {text}")
    return "\n".join(lines)
