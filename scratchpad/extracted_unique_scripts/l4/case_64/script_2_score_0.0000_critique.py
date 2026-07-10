import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_64/training_3.csv', index_col=0)

# Define join keys
join_keys = ['grade_range_cd_9-12', 'student_num', 'lea_avg_student_num', 'st_avg_student_num']

# Join source0 and source1 on join_keys (inner join to keep only matching keys)
joined_01 = pd.merge(source0, source1, on=join_keys, how='inner', suffixes=('_0', '_1'))

# Join joined_01 with source2
joined_012 = pd.merge(joined_01, source2, on=join_keys, how='inner', suffixes=('', '_2'))

# Join joined_012 with source3
joined_0123 = pd.merge(joined_012, source3, on=join_keys, how='inner', suffixes=('', '_3'))

# After join, columns from different sources may have suffixes or duplicates.
# We want to aggregate all columns except the join keys by max to reduce duplicates.

# Identify columns to aggregate (exclude join keys)
agg_columns = [col for col in joined_0123.columns if col not in join_keys]

# Aggregate by max for all non-key columns
agg_dict = {col: 'max' for col in agg_columns}

# Group by the join keys and aggregate
result = joined_0123.groupby(join_keys, as_index=False).agg(agg_dict)

# The target schema expects exact column names and types.
# Convert all columns to integer type as target schema is integer
# For columns with float NaNs, fill with 0 before converting to int
for col in result.columns:
    if col not in join_keys:
        # Fill NaN with 0 before converting to int
        result[col] = result[col].fillna(0).astype(int)
    else:
        # For join keys, also convert to int (if not already)
        result[col] = result[col].astype(int)

# Write to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_64/target_multisource_mcts.csv', index=False)