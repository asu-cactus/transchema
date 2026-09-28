import pandas as pd
import numpy as np

# Read source tables with index_col=0 to ignore the first index column
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_87/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_87/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_87/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_87/training_3.csv', index_col=0)

# The key columns to join on
join_keys = ['student_num']

# Perform successive inner joins on 'student_num'
df_joined = source0.merge(source1, on=join_keys, how='inner', suffixes=('_0', '_1'))
df_joined = df_joined.merge(source2, on=join_keys, how='inner', suffixes=('', '_2'))
df_joined = df_joined.merge(source3, on=join_keys, how='inner', suffixes=('', '_3'))

# The group by columns as per target schema leftmost unique integer columns
group_by_cols = ['grade_range_cd_9-12', 'student_num', 'lea_avg_student_num', 'st_avg_student_num']

# Some source tables may not have 'grade_range_cd_9-12' directly, so ensure it exists:
# If missing, try to get from source0 or source3 (source0 has grade_range_cd_9-12)
if 'grade_range_cd_9-12' not in df_joined.columns:
    # Try to get from source0 or source3 and merge
    if 'grade_range_cd_9-12' in source0.columns:
        df_joined = df_joined.merge(source0[['student_num', 'grade_range_cd_9-12']], on='student_num', how='left')
    elif 'grade_range_cd_9-12' in source3.columns:
        df_joined = df_joined.merge(source3[['student_num', 'grade_range_cd_9-12']], on='student_num', how='left')

# After join, some columns may have suffixes due to overlapping names; unify columns by taking mean of duplicates
# For columns with suffixes, average them and drop duplicates

def unify_columns(df):
    # Find base column names without suffixes
    base_cols = set()
    for col in df.columns:
        if col.endswith('_0') or col.endswith('_1') or col.endswith('_2') or col.endswith('_3'):
            base_cols.add(col[:-2])
        else:
            base_cols.add(col)
    base_cols = list(base_cols)

    unified = pd.DataFrame()
    for col in base_cols:
        # Find all columns matching this base col (with suffixes)
        matching_cols = [c for c in df.columns if c == col or c.startswith(col + '_')]
        if len(matching_cols) == 1:
            unified[col] = df[matching_cols[0]]
        else:
            # Take mean ignoring NaNs
            unified[col] = df[matching_cols].mean(axis=1)
    return unified

df_unified = unify_columns(df_joined)

# Now group by the key columns and aggregate others by mean
agg_cols = [col for col in df_unified.columns if col not in group_by_cols]

# Aggregate by mean
df_grouped = df_unified.groupby(group_by_cols, as_index=False)[agg_cols].mean()

# Cast all columns to int as target schema expects integers
for col in df_grouped.columns:
    if col not in group_by_cols:
        # Round before casting to int to avoid truncation errors
        df_grouped[col] = df_grouped[col].round().astype('Int64')

# Ensure group_by columns are int type as well
for col in group_by_cols:
    df_grouped[col] = df_grouped[col].astype('Int64')

# Write output to the target file
df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_87/target_multisource_mcts.csv', index=False)