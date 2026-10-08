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
    37: (
        "A target column does not have to come from exactly one source column. An "
        "aggregation's argument may be an arithmetic expression over several source "
        "columns -- AGG_FUNC(t.a + t.b + t.c) is valid anywhere AGG_FUNC(t.a) is. "
        "Consider a combination when no single source column matches the target "
        "column's name, or when the target's values are consistently larger than any "
        "one candidate source column's, or when the target's name reads as a category "
        "that several source columns fall under. Equally, do not force a combination "
        "when one source column already matches -- pick whichever the target's name, "
        "dtype and example values actually support."
    ),
    # --- Column-level operator (COLUMN_TRANSFORM) ---
    # 38/39 kept their original IDs through the COLUMN_AGGREGATION +
    # FORMAT_DATETIME + PROJECT -> COLUMN_TRANSFORM merge: only the operator each
    # one names changed, so existing ID lists and hint-number references in old
    # logs stay valid. Hint 40 (ex-PROJECT_HINT_IDS) was removed outright -- its
    # "do not use JOIN, PIVOT or GROUP_BY" framing was steering the model away
    # from a GROUP_BY that a case genuinely needed.
    38: (
        "When configuring COLUMN_TRANSFORM, give one entry per target column and "
        "choose which source columns feed it from what the target column's name and "
        "example values indicate -- a single target column may be fed by many source "
        "columns. Use SUM for quantities that add up and MAX/MIN for bounds, and prefer "
        "a combination only when no single source column already matches the target's "
        "name and values."
    ),
    39: (
        "If a date or time column is written differently in the target than in the "
        "source, use COLUMN_TRANSFORM to change it. If a target column is a part of a "
        "date (month, hour, season, day of week), use COLUMN_TRANSFORM to extract it "
        "first."
    ),
    41: (
        "If a target column's values match a source column but are written differently "
        "-- different case, padding, separator, or only part of the string -- use "
        "COLUMN_TRANSFORM to reshape the text with UPPER, LOWER, TRIM, CONCAT, SUBSTR, "
        "SPLIT or REPLACE. Compare against the target examples character-for-character "
        "before deciding."
    ),
}

# ---------------------------------------------------------------------------
# Per-prompt hint ID lists (from Current Prompt Mapping)
# ---------------------------------------------------------------------------

NEXT_OPERATOR_HINT_IDS = [1, 2, 3, 4, 5, 6, 9, 11, 16, 37, 39]
JOIN_HINT_IDS = [7, 8, 9, 35, 36]
GROUPBY_AGG_HINT_IDS = [10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22]
GROUPBY_HINT_IDS = [10, 11, 12, 13, 14]          # group-by column selection only
AGGREGATE_HINT_IDS = [14, 16, 17, 18, 19, 20, 21, 22, 33, 37]  # aggregation function selection only
# Single config group for COLUMN_TRANSFORM — the union of the former
# COLUMN_AGG_HINT_IDS [37, 38] and FORMAT_DATETIME_HINT_IDS [39], plus 41 for the
# newly added string functions. (Hint 40, ex-PROJECT_HINT_IDS, was removed
# outright -- see the note above.)
COLUMN_TRANSFORM_HINT_IDS = [37, 38, 39, 41]
# Config-only subset of the above: 39 is a ROUTING hint ("use COLUMN_TRANSFORM
# instead of X") that only makes sense while an operator is still being chosen.
# Simulate and Critique both act with the operator already fixed, so they get this
# subset (how to fill in / fix a COLUMNS: entry) rather than the full group.
COLUMN_TRANSFORM_CONFIG_HINT_IDS = [37, 38, 41]
PYTHON_SCRIPT_HINT_IDS = [1, 2, 3, 4, 5, 10, 11, 16, 17, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
CRITIQUE_HINT_IDS = [4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 33, 34, 35, 36]
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


def is_smartbuilding_dir(directory):
    """True when `directory` points at a smart_building benchmark root."""
    return "smartbuilding" in (directory or "")


def hints_for_benchmark(hint_ids, directory):
    """Drop hint #29 ("always add index_col=0") on smart_building.

    #29 is correct for github/monteprep, whose source CSVs carry a throwaway leading
    index column. smart_building's first column is REAL data (a date/CST column), so
    following #29 there makes the model read the source with index_col=0, which eats
    that column -- the subsequent rename/select then raises KeyError and the script
    produces no output at all. #29 sits in PIPELINE, PYTHON_SCRIPT and CRITIQUE id
    lists, so it poisons generation AND critique; filtering here covers all of them.
    """
    if is_smartbuilding_dir(directory):
        return [h for h in hint_ids if h != 29]
    return list(hint_ids)


def smartbuilding_override_for(directory, static_hints=True):
    """The counter-instruction text, or "" when it does not apply."""
    if is_smartbuilding_dir(directory) and static_hints:
        return get_smartbuilding_index_col_override()
    return ""


def get_smartbuilding_index_col_override():
    """Override text for the smart_building benchmark, whose source/target CSVs
    have NO throwaway leading index column (unlike github/monteprep, where hint
    #29 above -- "always add index_col=0" -- is correct). Following hint #29
    literally on smart_building data silently discards a real column (e.g. a
    date/CST column), which is exactly the bug this text heads off. Mirrors the
    override text already used in prompts/code_generation_prompt.py for the
    same benchmark/reason -- kept here as the single shared copy so new
    call sites (e.g. prompts/mcts_simulate.py) don't have to duplicate it.

    This is restored close to verbatim from the Simulate prompt logged in the
    2026-08-24 17/20 baseline run (smartbuilding_v2_first20_det_score_training),
    from before the COLUMN_AGGREGATION/FORMAT_DATETIME/PROJECT -> COLUMN_TRANSFORM
    merge. The only change from that original text is the dow paragraph's example
    API call: it originally read "date.isoweekday()", which -- as that very log
    shows -- raises AttributeError when called through pandas' vectorized .dt
    accessor (.dt has no isoweekday); the model self-corrected on retry, but the
    example itself was wrong. Replaced with the equivalent vectorized form,
    (parsed_date.dt.dayofweek + 1), with everything else left as it was.
    """
    return (
        "\nImportant: do NOT use index_col=0 when reading the source CSV, and do NOT "
        "drop its first column. Every column in this benchmark's source and target "
        "files is real data — there is no throwaway leading index column.\n"
        "\nBefore finalizing, re-check every string/date output column "
        "character-for-character against the Target Examples shown above (YOUR "
        "CURRENT task's own target samples — NOT a retrieved similar-case example's "
        "samples, which use different, unrelated data and formatting that may not "
        "apply here). Do not simply copy a source column as-is if YOUR OWN target "
        "sample shows extra formatting; conversely, do NOT invent formatting (like a "
        "weekday abbreviation) that YOUR OWN target sample does not actually show.\n"
        "If — and only if — your current task's own Target Examples show a date "
        "column with a 3-letter weekday abbreviation (e.g. 'Sat 01/01/2011') that "
        "the source column's own sample values do NOT contain, you must COMPUTE it "
        "— derive it from the parsed date, e.g.:\n"
        "    d = pd.to_datetime(df['date_col'])\n"
        "    df['CST'] = d.dt.strftime('%a') + ' ' + d.dt.strftime('%m/%d/%Y')\n"
        "This applies even if the source has a separate column that already encodes "
        "one PART of the target value (e.g. a numeric day-of-week column): count how "
        "many distinct parts your current task's OWN target sample string actually "
        "has, and make sure your output concatenates ALL of them — never substitute "
        "one part alone (e.g. just the mapped weekday name) for the full multi-part "
        "value.\n"
        "Zero-pad month/day (e.g. '01' not '1') the same way — via strftime, not "
        "string concatenation of the raw parsed components.\n"
        "\nNEVER produce a date/datetime output column via a bare str(...), "
        ".astype(str), or default to_csv serialization of a datetime/Timestamp "
        "value — pandas' default string form is ISO format ('2011-01-01'), which is "
        "almost never what this benchmark's targets actually want (they use forms "
        "like '1/1/2011', '04/01/09', 'Sat 01/01/2011', etc., each with its own "
        "separators/padding/year-length). Always convert explicitly with "
        ".dt.strftime('<format matching your own target sample exactly>') and derive "
        "that format string by inspecting your own target sample's literal "
        "characters (digit count for year, presence of leading zeros, separator "
        "characters, weekday or not) — never guess or default.\n"
        "\nReproduce string/categorical output values EXACTLY as they appear in "
        "your own target sample, including any leading/trailing whitespace or "
        "fixed-width padding (e.g. a month name padded to 9 characters like "
        "'January  ' with two trailing spaces). Do not strip, trim, or normalize "
        "whitespace unless your own target sample itself shows it stripped — pad "
        "with .ljust(width) or equivalent if the sample shows fixed-width padding, "
        "using the exact width observed.\n"
        "\nIf a target column is a numeric day-of-week integer (name like 'dow' or "
        "similar), do NOT assume pandas' default .dt.dayofweek / .weekday() "
        "convention (Monday=0). Verify against your own target sample: pick one "
        "target sample row whose date you can identify, work out that date's real "
        "day of the week, and check what integer the sample uses for it. Many "
        "SQL-derived targets in this benchmark use EXTRACT(ISODOW)-style numbering "
        "(Monday=1 ... Sunday=7) or EXTRACT(DOW)-style (Sunday=0 ... Saturday=6) "
        "instead — confirm which one matches your sample before writing the "
        "conversion, e.g. via (parsed_date.dt.dayofweek + 1) (Mon=1..Sun=7) or "
        "(parsed_date.dt.dayofweek + 1) % 7 (Sun=0..Sat=6), not a blind .weekday() "
        "call.\n"
    )
