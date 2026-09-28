import pandas as pd

# Read all source CSVs with index_col=0
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_62/training_3.csv', index_col=0)

# Define join keys
join_keys = ['student_num', 'lea_avg_student_num', 'st_avg_student_num', 'unit_code', 'year']

# Join source0 and source1 on join_keys
joined_01 = pd.merge(source0, source1, on=join_keys, how='inner', suffixes=('', '_s1'))

# Join joined_01 and source2 on join_keys
joined_012 = pd.merge(joined_01, source2, on=join_keys, how='inner', suffixes=('', '_s2'))

# Join joined_012 and source3 on join_keys
joined_all = pd.merge(joined_012, source3, on=join_keys, how='inner', suffixes=('', '_s3'))

# Prepare aggregation:
# Group by the join keys
group_by_cols = join_keys

# Identify all columns except group_by_cols for aggregation
agg_cols = [col for col in joined_all.columns if col not in group_by_cols]

# For aggregation, sum all numeric columns except group_by_cols
# If any columns are non-numeric, ignore or convert to numeric with errors='coerce'
# We will sum numeric columns, ignoring non-numeric columns (if any)
numeric_cols = joined_all[agg_cols].select_dtypes(include=['number']).columns.tolist()

# Aggregate by sum on numeric columns
agg_dict = {col: 'sum' for col in numeric_cols}

# Perform groupby aggregation
result = joined_all.groupby(group_by_cols, as_index=False).agg(agg_dict)

# The target schema expects exact column names without suffixes.
# The join added suffixes for overlapping columns from source1, source2, source3.
# We must rename columns to match target schema exactly.
# The target schema columns are from all sources combined without suffixes.
# So we rename columns by removing suffixes _s1, _s2, _s3 if present.

def remove_suffix(col):
    for suffix in ['_s1', '_s2', '_s3']:
        if col.endswith(suffix):
            return col[:-len(suffix)]
    return col

result.columns = [remove_suffix(col) for col in result.columns]

# Save the final result to the target CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_62/target_multisource_mcts.csv', index=False)