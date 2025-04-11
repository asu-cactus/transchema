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
