from util.utils import are_elements_equal

def convert_if_number(s):
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return s



def compare_columns(pred_column, gold_column):
    # Convert all elements to strings for consistent comparison
    pred_column = [str(x) if x is not None else '' for x in pred_column]
    gold_column = [str(x) if x is not None else '' for x in gold_column]
    
    # Sort the columns
    pred_column.sort()
    gold_column.sort()
    
    # Count matches
    matches = sum(1 for p, g in zip(pred_column, gold_column) if are_elements_equal(p, g))
    total = len(pred_column)
    
    return matches / total if total > 0 else 0

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

def compare_lists_matching(generated_sql_df, ground_truth_df):
    #print("Sorting")

    generated_sql_df = generated_sql_df.loc[
        :, ~generated_sql_df.columns.duplicated()
    ].copy()
    generated_sql_df = generated_sql_df.sort_values(by=list(generated_sql_df.columns))
    ground_truth_df = ground_truth_df.sort_values(by=list(ground_truth_df.columns))

    #print("Comparing column lengths")

    if len(generated_sql_df.columns) == 0 or len(ground_truth_df.columns) == 0:
        return (
            0,
            False,
            ["mismatch"],
            ["Mismatch - No columns in one or both DataFrames"],
        )

    #print("Comparing row lengths")

    if len(generated_sql_df) != len(ground_truth_df):
        return (
            0,
            False,
            ["mismatch"],
            [
                f"Mismatch - DataFrames lengths differ (pred:{len(generated_sql_df)} v.s. gold:{len(ground_truth_df)})"
            ],
        )

    similarities = []
    all_mismatches = []

    num_cols = len(generated_sql_df.columns)

    for col in generated_sql_df.columns:

        # #print(col)
        if col.find("Unnamed: 0") >= 0:
            #print("skip " + col)
            num_cols -= 1
            continue

        pred_column = generated_sql_df[col].tolist()
        if(col in ground_truth_df.columns):
            gold_column = ground_truth_df[col].tolist()
        else : 
            column_similarity = 0
            similarities.append(column_similarity)
            continue

        # Use the updated function to determine if the column is numerically dominant
        is_numerical = is_column_numerically_dominant(generated_sql_df[col])

        # #print(is_numerical)

        # #print(pred_column)

        # #print(gold_column)

        # Use the updated compare_columns function
        column_similarity = compare_columns(pred_column, gold_column)

        similarities.append(column_similarity)

        if column_similarity < 1:
            mismatches = [
                {
                    "<col, row>": "<" + str(col) + ", " + str(i) + ">",
                    "pred": pred_column[i],
                    "gold": gold_column[i],
                }
                for i in range(len(pred_column))
                if not are_elements_equal(pred_column[i], gold_column[i])
            ]
            all_mismatches.append((col, mismatches))

    average_similarity = sum(similarities) / num_cols
    res = average_similarity == 1

    return average_similarity, res, similarities, all_mismatches