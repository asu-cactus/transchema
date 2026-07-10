import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)

group_cols = [
    'CANCELED', 'SES', 'CITY', 'POP', 'CANCEL_DT', 'CUST_SINCE_DT'
]

# We have multiple sources with similar schema: s3, s5, s6, s7
# We will rename columns to distinguish them before joining/grouping

def rename_cols(df, suffix):
    cols = df.columns.tolist()
    rename_map = {}
    for c in cols:
        if c in ['ARPU', 'CANCELED', 'SES', 'CITY', 'POP', 'CANCEL_DT', 'CUST_SINCE_DT']:
            rename_map[c] = f"{c}_{suffix}"
    return df.rename(columns=rename_map)

s3_r = rename_cols(s3, "3")
s5_r = rename_cols(s5, "5")
s6_r = rename_cols(s6, "6")
s7_r = rename_cols(s7, "7")

# Merge on ROW_WID to align rows (inner join to keep only matching ROW_WID)
# But the partial plan groups by many columns from all sources, so we join on ROW_WID and all these columns

# First, merge s3 and s5 on ROW_WID and common columns
merge_cols_35 = ['ROW_WID']
# For grouping, we need to join on columns that appear in group_by from both sources
# From partial plan, group_by includes:
# Source9_28_3: CANCELED, SES, CITY, POP, CANCEL_DT
# Source9_28_5: CANCELED, SES, CANCEL_DT, CITY, POP, CUST_SINCE_DT
# So join on ROW_WID and these columns to align rows properly

# To join on these columns, we need to rename columns back to original names for join keys
# So create key columns for join by stripping suffixes temporarily

def prepare_keys(df, suffix):
    df_keys = df.copy()
    for col in ['CANCELED', 'SES', 'CITY', 'POP', 'CANCEL_DT', 'CUST_SINCE_DT']:
        suffixed = f"{col}_{suffix}"
        if suffixed in df_keys.columns:
            df_keys[col] = df_keys[suffixed]
    return df_keys

s3_keys = prepare_keys(s3_r, "3")
s5_keys = prepare_keys(s5_r, "5")
s6_keys = prepare_keys(s6_r, "6")
s7_keys = prepare_keys(s7_r, "7")

# Merge s3 and s5 on ROW_WID and keys columns that exist in both
common_keys_35 = ['ROW_WID', 'CANCELED', 'SES', 'CITY', 'POP', 'CANCEL_DT', 'CUST_SINCE_DT']
s35 = pd.merge(s3_keys, s5_keys, on=common_keys_35, suffixes=('_3', '_5'))

# Merge s35 with s6
common_keys_6 = ['ROW_WID', 'CANCELED', 'SES', 'CITY', 'POP', 'CANCEL_DT', 'CUST_SINCE_DT']
s6_keys_sub = s6_keys[common_keys_6 + [f"ARPU_6"]]
s356 = pd.merge(s35, s6_keys_sub, on=common_keys_6, how='inner')

# Merge s356 with s7
common_keys_7 = ['ROW_WID', 'CANCELED', 'SES', 'CITY', 'POP', 'CANCEL_DT', 'CUST_SINCE_DT']
s7_keys_sub = s7_keys[common_keys_7 + [f"ARPU_7"]]
s3567 = pd.merge(s356, s7_keys_sub, on=common_keys_7, how='inner')

# Now compute average ARPU from the four sources
# ARPU columns: ARPU_3, ARPU_5, ARPU_6, ARPU_7
# Some ARPU columns may be missing or NaN, so average only non-null values

arpu_cols = ['ARPU_3', 'ARPU_5', 'ARPU_6', 'ARPU_7']
s3567['ARPU_3'] = s3567['ARPU_3'].astype(float)
s3567['ARPU_5'] = s3567['ARPU_5'].astype(float)
s3567['ARPU_6'] = s3567['ARPU_6'].astype(float)
s3567['ARPU_7'] = s3567['ARPU_7'].astype(float)

s3567['ARPU'] = s3567[arpu_cols].mean(axis=1)

# The target schema is ['ARPU'] only
target = s3567[['ARPU']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)