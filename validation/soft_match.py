# from padding_match import pad_comp
from util.utils import are_elements_equal
from collections import Counter
import bisect
import pandas as pd

def pad_comp(target_df, attempt_df):
    # Step 1: Padding columns
    target_columns = target_df.columns
    attempt_columns = attempt_df.columns
    
    # Add padding columns if needed
    padding_value = "cluegideluxxi"
    if len(target_columns) > len(attempt_columns):
        for i in range(len(target_columns) - len(attempt_columns)):
            attempt_df[f"extra_{i+1}"] = padding_value
    elif len(attempt_columns) > len(target_columns):
        for i in range(len(attempt_columns) - len(target_columns)):
            target_df[f"extra_{i+1}"] = padding_value

    # Fix row count mismatch
    if len(target_df) > len(attempt_df):
        # Add padding rows to attempt_df
        pad_row = {col: padding_value for col in attempt_df.columns}
        rows_to_add = len(target_df) - len(attempt_df)
        padding_df = pd.DataFrame([pad_row] * rows_to_add)
        attempt_df = pd.concat([attempt_df, padding_df], ignore_index=True)
    elif len(attempt_df) > len(target_df):
        # Add padding rows to target_df
        pad_row = {col: padding_value for col in target_df.columns}
        rows_to_add = len(attempt_df) - len(target_df)
        padding_df = pd.DataFrame([pad_row] * rows_to_add)
        target_df = pd.concat([target_df, padding_df], ignore_index=True)
    
    # Step 2: Sorting and correlating columns
    target_columns_sorted = sorted(target_df.columns)
    attempt_columns_sorted = sorted(attempt_df.columns)
    
    # Create correlated column order
    correlated_target_cols = []
    correlated_attempt_cols = []
    unmatched_target_cols = []
    unmatched_attempt_cols = []
    
    # Match target columns to attempt columns based on substring
    for tcol in target_columns_sorted:
        matched = False
        for acol in attempt_columns_sorted:
            if tcol in acol:
                correlated_target_cols.append(tcol)
                correlated_attempt_cols.append(acol)
                attempt_columns_sorted.remove(acol)
                matched = True
                break
        if not matched:
            unmatched_target_cols.append(tcol)
    
    # Add unmatched attempt columns
    correlated_target_cols.extend(unmatched_target_cols)
    correlated_attempt_cols.extend(attempt_columns_sorted)
    
    # Step 3: Reorder columns in DataFrames
    target_df = target_df[correlated_target_cols]
    attempt_df = attempt_df[correlated_attempt_cols]

    # Step 4: Matching names
    attempt_df.columns = target_df.columns
    
    return attempt_df, target_df


def find_best_matching_column(pred_col, ground_truth_df):
    max_matches = -1
    best_col = None

    for gt_col in ground_truth_df.columns:
        gt_values = ground_truth_df[gt_col].dropna().astype(str).tolist()
        pred_values = pred_col.dropna().astype(str).tolist()
        common = set(gt_values) & set(pred_values)
        if len(common) > max_matches:
            max_matches = len(common)
            best_col = gt_col

    return best_col


def compare_columns_1(pred_column, gold_column, tol=0.001):
    # --- 1) Split into numeric vs “everything else” ---
    pred_non = []
    pred_nums = []
    for x in pred_column:
        if x is None:
            pred_non.append("")
        elif isinstance(x, (int, float)):
            pred_nums.append(float(x))
        else:
            pred_non.append(str(x))

    gold_non = []
    gold_nums = []
    for x in gold_column:
        if x is None:
            gold_non.append("")
        elif isinstance(x, (int, float)):
            gold_nums.append(float(x))
        else:
            gold_non.append(str(x))

    # --- 2) Exact‐match recall on non‐numeric ---
    pred_non_freq = Counter(pred_non)
    gold_non_freq = Counter(gold_non)
    matched_non = sum(min(pred_non_freq[v], gold_non_freq[v]) for v in gold_non_freq)

    # --- 3) Approximate‐match recall on numeric (ints+floats) ---
    pred_nums.sort()
    matched_nums = 0
    for g in gold_nums:
        i = bisect.bisect_left(pred_nums, g)

        # Search nearby values for the closest match within tolerance
        best_j = -1
        best_dist = float("inf")

        for j in range(
            max(0, i - 3), min(len(pred_nums), i + 3)
        ):  # widen search window if needed
            dist = abs(pred_nums[j] - g)
            if dist <= tol and dist < best_dist:
                best_dist = dist
                best_j = j

        if best_j != -1:
            matched_nums += 1
            pred_nums.pop(best_j)  # consume matched prediction
        # else:
        #     print(f"Failed to match {g} in {pred_nums} with tolerance {tol}")

    # print(pred_nums, matched_nums)

    # --- 4) Combine and return recall over all gold values ---
    total_gold = len(gold_column)
    total_matched = matched_non + matched_nums
    return total_matched / total_gold if total_gold > 0 else 0.0


def compare_lists_matching_soft(ground_truth_df, generated_sql_df, padding_added=False):
    # Remove duplicate columns and sort
    generated_sql_df = generated_sql_df.loc[
        :, ~generated_sql_df.columns.duplicated()
    ].copy()
    generated_sql_df = generated_sql_df.sort_values(by=list(generated_sql_df.columns))
    ground_truth_df = ground_truth_df.sort_values(by=list(ground_truth_df.columns))
    # print("WOOP WOOP WOOP")
    # Only pad if we haven't already done so
    if not padding_added:
        if (
            len(generated_sql_df.columns) == 0
            or len(ground_truth_df.columns) == 0
            or len(generated_sql_df) != len(ground_truth_df)
        ):
            padded_dfs = pad_comp(ground_truth_df, generated_sql_df)
            return compare_lists_matching_soft(*padded_dfs, padding_added=True)

    # generated_sql_df, ground_truth_df = pad_comp(generated_sql_df, ground_truth_df)

    similarities = []
    all_mismatches = []
    num_cols = 0

    for col in generated_sql_df.columns:
        if col.find("Unnamed: 0") >= 0:
            continue

        num_cols += 1
        pred_column = generated_sql_df[col].tolist()
        pred_col = generated_sql_df[col]
        if col not in ground_truth_df.columns:
            best_match_col = find_best_matching_column(pred_col, ground_truth_df)
            if best_match_col is not None:
                gold_column = ground_truth_df[best_match_col].tolist()
            else:
                continue
        else:
            gold_column = ground_truth_df[col].tolist()

        # print(pred_column)
        # print(gold_column)

        column_similarity = compare_columns_1(pred_column, gold_column)
        similarities.append(column_similarity)

        if column_similarity < 1:
            mismatches = [
                {
                    "<col, row>": f"<{col}, {i}>",
                    "pred": pred_column[i],
                    "gold": gold_column[i],
                }
                for i in range(len(pred_column))
                if not are_elements_equal(pred_column[i], gold_column[i])
            ]
            all_mismatches.append((col, mismatches))

    if num_cols == 0:
        return 0, False, []

    average_similarity = sum(similarities) / num_cols
    res = average_similarity == 1

    return average_similarity, res, similarities


if __name__ == "__main__":
    gt_df = pd.read_csv(
        "autopipeline-benchmarks/github-pipelines/length1_23/target.csv"
    )
    gen_df = pd.read_csv(
        "autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_critique_soft.csv"
    )
    avg_sim, is_exact, sim_list = compare_lists_matching_soft(gt_df, gen_df)
    print(f"Average Similarity: {avg_sim}")
    print(f"Is Exact Match: {is_exact}")
