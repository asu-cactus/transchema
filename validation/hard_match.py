import math
from validation.autopipeline_match import compare_tables


def _convert_if_number(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def are_elements_equal(elem1, elem2, tolerance=1e-1):
    elem1 = "" if elem1 is None else elem1
    elem2 = "" if elem2 is None else elem2
    elem1 = _convert_if_number(elem1)
    elem2 = _convert_if_number(elem2)
    if isinstance(elem1, float) and isinstance(elem2, float):
        denom = max(abs(elem1), abs(elem2))
        if denom == 0:
            return True
        return (abs(elem1 - elem2) / denom) < tolerance
    if isinstance(elem1, str) and isinstance(elem2, str):
        return elem1.strip().lower() == elem2.strip().lower()
    return elem1 == elem2


def is_string_nan(s):
    try:
        f = float(s)
        return math.isnan(f)
    except ValueError:
        return False


def compare_columns(pred_column, gold_column):
    # Convert all elements to strings for consistent comparison
    pred_column = [
        str(x).lower() if x is not None and is_string_nan(x) == False else "N/A"
        for x in pred_column
    ]
    gold_column = [
        str(x).lower() if x is not None and is_string_nan(x) == False else "N/A"
        for x in gold_column
    ]

    # Sort the columns
    pred_column.sort()
    gold_column.sort()

    # Count matches
    matches = sum(
        1
        for p, g in zip(pred_column, gold_column)
        if are_elements_equal(p, g) and p != "nan" and g != "nan"
    )
    print("num matches:", matches)
    total = len(pred_column)
    print("total:", total)
    print("non-matching tuples:")
    # for p, g in zip(pred_column, gold_column):
    #   if are_elements_equal(p, g) == False:
    #     print(p)
    #    print(g)
    #   print("\n")
    return matches / total if total > 0 else 1 / (1 - (total - matches))


def compare_numerical_columns(pred_column, gold_column):
    # Convert all elements to strings for consistent comparison
    pred_column = [float(x) for x in pred_column]
    gold_column = [float(x) for x in gold_column]

    # Sort the columns
    pred_column.sort()
    gold_column.sort()

    # Count matches
    matches = sum(
        1
        for p, g in zip(pred_column, gold_column)
        if abs(p - g) < 0.01 or (math.isnan(p) == True and math.isnan(g) == True)
    )
    print("num matches:", matches)
    total = len(pred_column)
    print("total:", total)
    print("non-matching tuples:")
    # for p, g in zip(pred_column, gold_column):
    #   if p - g >= 0.01:
    #      print(str(p)+"<->"+str(g)+";")
    return matches / total if total > 0 else 1 / (1 - (total - matches))


def is_column_numerical(column):
    numeric_count = 0
    total_count = len(column)
    for val in column:
        try:
            float(val)
            numeric_count += 1
        except (ValueError, TypeError):
            if val == "":
                total_count -= 1  # do not consider empty string
    return numeric_count == total_count  # all values are numeric


def is_column_numerically_dominant(column):
    numeric_count = 0
    total_count = len(column)
    for val in column:
        try:
            float(val)
            numeric_count += 1
        except (ValueError, TypeError):
            if val == "":
                total_count -= 1  # do not consider empty string
    return numeric_count / total_count > 0.5  # Majority of values are numeric


def intersection_high_precision_floats(list1, list2, rel_tol=1e-09, abs_tol=0.0):
    """
    Finds the intersection of two lists of high-precision floats using math.isclose().

    Args:
        list1 (list): The first list of floats.
        list2 (list): The second list of floats.
        rel_tol (float): The relative tolerance for approximate equality.
        abs_tol (float): The absolute tolerance for approximate equality.

    Returns:
        list: A new list containing the common elements.
    """
    intersection = []
    for num1 in list1:
        for num2 in list2:
            if math.isclose(num1, num2, rel_tol=rel_tol, abs_tol=abs_tol):
                intersection.append(num1)
                break  # Move to the next element in list1 once a match is found
    return intersection


def compare_lists_matching(generated_sql_df, ground_truth_df):
    # Drop duplicate columns
    generated_duplicate_cols = generated_sql_df.columns[
        generated_sql_df.columns.duplicated()
    ]
    generated_sql_df = generated_sql_df.drop(columns=generated_duplicate_cols)
    generated_sql_df = generated_sql_df.sort_values(by=list(generated_sql_df.columns))
    ground_truth_duplicate_cols = ground_truth_df.columns[
        ground_truth_df.columns.duplicated()
    ]
    ground_truth_df = ground_truth_df.drop(columns=ground_truth_duplicate_cols)
    ground_truth_df = ground_truth_df.sort_values(by=list(ground_truth_df.columns))
    generated_sql_df = generated_sql_df.drop_duplicates()
    ground_truth_df = ground_truth_df.drop_duplicates()

    # Drop index artifacts upfront — cleaner than the mid-loop find() hack
    try:
        generated_sql_df = generated_sql_df.drop("Unnamed: 0", axis=1)
    except KeyError:
        pass
    try:
        ground_truth_df = ground_truth_df.drop("Unnamed: 0", axis=1)
    except KeyError:
        pass

    if len(generated_sql_df.columns) == 0 or len(ground_truth_df.columns) == 0:
        print("Mismatch - No columns in one or both DataFrames")
        return (
            0,
            False,
            ["Mismatch - No columns in one or both DataFrames"],
            [],
        )

    # Column schema mismatch — compute partial credit on intersection, but always return False
    col_mismatch = False
    if len(generated_sql_df.columns) != len(ground_truth_df.columns):
        print(
            f"Mismatch - Column counts differ (pred:{len(generated_sql_df.columns)} v.s. gold:{len(ground_truth_df.columns)})"
        )
        col_mismatch = True
    elif set(generated_sql_df.columns) != set(ground_truth_df.columns):
        pred_extra = set(generated_sql_df.columns) - set(ground_truth_df.columns)
        gold_extra = set(ground_truth_df.columns) - set(generated_sql_df.columns)
        print(
            f"Mismatch - Column names differ (pred_extra:{pred_extra} v.s. gold_extra:{gold_extra})"
        )
        col_mismatch = True

    if col_mismatch:
        # Restrict to columns present in both — missing gold columns score 0 via num_cols denominator
        shared_cols = set(generated_sql_df.columns) & set(ground_truth_df.columns)
        generated_sql_df = generated_sql_df[list(shared_cols)]
        num_cols = len(
            ground_truth_df.columns
        )  # denominator is gold schema size, not intersection

    half_comparison = False

    if len(generated_sql_df) != len(ground_truth_df):
        print(
            f"Mismatch - DataFrames lengths differ (pred:{len(generated_sql_df)} v.s. gold:{len(ground_truth_df)})"
        )
        # For case 9_20, the ground truth is wrong, it also includes tuples transformed from the training data, we shall exclude such cases
        if (
            len(generated_sql_df) != len(ground_truth_df) / 2
            and len(generated_sql_df) != len(ground_truth_df) / 2 + 1
        ):
            return (
                0,
                False,
                [
                    f"Mismatch - DataFrames lengths differ (pred:{len(generated_sql_df)} v.s. gold:{len(ground_truth_df)})"
                ],
                [],
            )
        else:
            half_comparison = True

    similarities = []
    all_matches = []
    num_cols = (
        len(ground_truth_df.columns) if col_mismatch else len(generated_sql_df.columns)
    )

    for col in generated_sql_df.columns:

        print(col)

        pred_column = generated_sql_df[col].tolist()
        if col in ground_truth_df.columns:
            gold_column = ground_truth_df[col].tolist()
        else:
            print("column does not exist in ground truth")
            column_similarity = 0
            similarities.append(column_similarity)
            continue

        # Use the updated function to determine if the column is numerically dominant
        is_generated_numerical = is_column_numerical(generated_sql_df[col])
        is_gold_numerical = is_column_numerical(ground_truth_df[col])
        is_numerical = is_generated_numerical and is_gold_numerical
        print(is_numerical)

        if half_comparison:
            s1 = {
                x for x in pred_column if not (isinstance(x, float) and math.isnan(x))
            }
            s2 = {
                x for x in gold_column if not (isinstance(x, float) and math.isnan(x))
            }
            if is_numerical:
                intersection = intersection_high_precision_floats(s1, s2)
            else:
                intersection = s1.intersection(s2)
            column_similarity = float(len(intersection)) / float(len(s1))
            if 1 - column_similarity > 0.001:
                print(s1 - intersection)
                print("=======")
                print(s2)
        else:
            if is_numerical:
                column_similarity = compare_numerical_columns(pred_column, gold_column)
            else:
                column_similarity = compare_columns(pred_column, gold_column)

        if 1 - column_similarity < 0.001:
            all_matches.append(col)

        similarities.append(column_similarity)

    print("COLUMN SIMILARITY:")
    print(similarities)
    average_similarity = sum(similarities) / num_cols
    res = average_similarity == 1 and not col_mismatch

    print("AVERAGE COLUMN SIMILARITY:", str(average_similarity))
    return average_similarity, res, similarities, all_matches


def compare_tables_matching(df_generate, df_target):
    """Adapter that wraps compare_tables() to return the same 4-tuple as
    compare_lists_matching: (average_similarity, is_correct, similarity_scores, matched_cols).

    Note: compare_tables is binary (no per-column partial credit), so
    average_similarity and similarity_scores are always 1.0 or 0.0.
    """
    is_match, matched_cols = compare_tables(df_generate, df_target)
    average_similarity = 1.0 if is_match else 0.0
    similarity_scores = [average_similarity] * len(df_target.columns)
    return average_similarity, is_match, similarity_scores, matched_cols
