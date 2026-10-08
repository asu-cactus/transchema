import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_3.csv', index_col=0)

# The join keys common to all sources
join_keys = ['student_num', 'lea_avg_student_num', 'st_avg_student_num']

# Join source0 and source1 on join_keys (inner join to keep only matching keys)
joined_01 = pd.merge(source0, source1, on=join_keys, how='inner', suffixes=('_0', '_1'))

# Join with source2
joined_012 = pd.merge(joined_01, source2, on=join_keys, how='inner', suffixes=('', '_2'))

# Join with source3
joined_0123 = pd.merge(joined_012, source3, on=join_keys, how='inner', suffixes=('', '_3'))

# After join, columns from different sources may have suffixes or duplicates.
# We want to produce the target schema exactly, so:
# 1. Identify the group by columns: grade_range_cd_9-12, student_num, lea_avg_student_num, st_avg_student_num
#    grade_range_cd_9-12 may be missing in source0, so it may have NaNs after join.
# 2. Aggregate all other columns by sum (excluding group by columns).
# 3. Convert all columns to integer as target schema requires integer.

# Ensure 'grade_range_cd_9-12' is present (some sources have it, source0 does not)
# It may have NaNs due to source0 missing it; keep as is for grouping.

# Define group by columns
group_by_cols = ['grade_range_cd_9-12', 'student_num', 'lea_avg_student_num', 'st_avg_student_num']

# Some columns may have suffixes from merges; unify columns by removing suffixes for aggregation
# For columns with suffixes, sum them together.

# First, get all columns except group_by_cols
all_cols = set(joined_0123.columns)
non_key_cols = list(all_cols - set(group_by_cols))

# For columns with suffixes, we need to sum them together into one column without suffix
# Strategy:
# - For each base column name (without suffix), sum all columns that start with that base name
# - For example, 'lea_total_expense_num', 'lea_total_expense_num_1', 'lea_total_expense_num_2', 'lea_total_expense_num_3'
#   sum all these columns into one 'lea_total_expense_num'

# Extract base column names by removing suffixes like _0, _1, _2, _3
def base_col_name(col):
    for suffix in ['_0', '_1', '_2', '_3']:
        if col.endswith(suffix):
            return col[:-2]
    return col

# Map base column to list of columns in joined_0123
from collections import defaultdict
base_col_map = defaultdict(list)
for col in non_key_cols:
    base = base_col_name(col)
    base_col_map[base].append(col)

# For aggregation, sum all columns in each base_col_map entry
agg_dict = {}
for base_col, cols in base_col_map.items():
    agg_dict[base_col] = lambda df, cols=cols: df[cols].sum(axis=1)

# Create a DataFrame with group_by columns and aggregated columns
# First, keep group_by columns
df_group = joined_0123[group_by_cols].copy()

# Compute aggregated columns
for base_col, func in agg_dict.items():
    df_group[base_col] = func(joined_0123)

# Now group by the group_by_cols and sum aggregated columns (to handle duplicates)
agg_cols = list(base_col_map.keys())
df_final = df_group.groupby(group_by_cols, dropna=False)[agg_cols].sum().reset_index()

# Convert all columns to integer as per target schema
# For columns with NaN, fill with 0 before converting to int
df_final = df_final.fillna(0)
for col in df_final.columns:
    df_final[col] = df_final[col].astype(int)

# Write to output CSV
df_final.to_csv('autopipeline-benchmarks/github-pipelines/length4_64/target_multisource_mcts.csv', index=False)