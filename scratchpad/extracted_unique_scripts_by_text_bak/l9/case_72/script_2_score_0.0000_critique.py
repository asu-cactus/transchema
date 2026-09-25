import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_72/training_9.csv", index_col=0)

# Union all tables with the same schema (Sources 0,1,3,4,5,7,8,9)
# They share the same columns, but s5 has extra columns '5040' and '100.00%', so drop them to align schemas
cols_to_keep = s0.columns.intersection(s5.columns).tolist()
# For s5, drop extra columns to match s0 schema
s5_trimmed = s5[cols_to_keep]

# Similarly, s5 trimmed columns should be consistent with others
# For safety, align all union tables columns to s0 columns
def align_columns(df, reference_cols):
    # Keep only columns in reference_cols, add missing columns with NaN
    df = df.copy()
    for c in reference_cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[reference_cols]

union_tables = [s0, s1, s3, s4, s5_trimmed, s7, s8, s9]
union_tables_aligned = [align_columns(df, s0.columns) for df in union_tables]

unioned = pd.concat(union_tables_aligned, ignore_index=True)

# Join unioned with s2 on bid_id = sampled_bid_id and message_timestamp
joined_1 = pd.merge(
    unioned,
    s2,
    how='inner',
    left_on=['bid_id', 'message_timestamp'],
    right_on=['sampled_bid_id', 'message_timestamp'],
    suffixes=('', '_s2')
)
joined_1.drop(columns=['sampled_bid_id'], inplace=True)

# Join the above with s6 on bid_id and message_timestamp
final_join = pd.merge(
    joined_1,
    s6,
    how='inner',
    on=['bid_id', 'message_timestamp'],
    suffixes=('', '_s6')
)

# Group by bid_id and message_timestamp to remove duplicates and ensure uniqueness
# No aggregation columns specified, so just drop duplicates based on these keys
final = final_join.drop_duplicates(subset=['bid_id', 'message_timestamp'])

# The target schema has many columns with suffixes due to multiple joins.
# To match the target schema exactly, we must rename columns accordingly.
# However, the problem states: "Keep column names exactly as in the target schema (no added prefixes/suffixes)."
# The target schema shows columns like 'message_sender_x', 'message_sender_y', etc.
# So we must rename columns to match these suffixes.

# To do this, we will rename columns from each source accordingly:
# unioned columns: suffix '_x' (from unioned)
# s2 columns: suffix '_y' (from s2)
# s6 columns: suffix '' or '_z' (we can use '_z' or no suffix)

# But since unioned is from multiple sources, and target schema has multiple suffixes,
# the target schema shows multiple repeated suffixes, indicating multiple joins of similar tables.
# Given complexity, and since the target schema is very wide with many repeated suffixes,
# the best we can do is to rename columns from unioned as '_x', from s2 as '_y', and from s6 as no suffix.

# Rename unioned columns (except join keys) with '_x'
unioned_cols = s0.columns.tolist()
unioned_cols.remove('bid_id')
unioned_cols.remove('message_timestamp')
rename_union = {col: col + '_x' for col in unioned_cols}

# Rename s2 columns (except join keys) with '_y'
s2_cols = s2.columns.tolist()
s2_cols.remove('sampled_bid_id')
s2_cols.remove('message_timestamp')
rename_s2 = {col: col + '_y' for col in s2_cols}

# Rename s6 columns (except join keys) with '_z' (to avoid conflict)
s6_cols = s6.columns.tolist()
s6_cols.remove('bid_id')
s6_cols.remove('message_timestamp')
rename_s6 = {col: col + '_z' for col in s6_cols}

# Apply renaming
final = final.rename(columns={**rename_union, **rename_s2, **rename_s6})

# Rename join keys to match target schema exactly
# Target schema keys: 'bid_id' (int), 'message_timestamp' (string)
# Keep as is

# Write to CSV
final.to_csv("autopipeline-benchmarks/github-pipelines/length9_72/target_multisource_mcts.csv", index=False)