import pandas as pd
from functools import reduce

# Read all source CSVs with index_col=0 to ignore the numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

# Rename columns to avoid conflicts except the key column '2012-12-05'
# Actually, all source tables have schema ['2012-12-05', <value_column>]
# We will join on '2012-12-05' and keep all value columns with their original names

# List of all dataframes
dfs = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]

# Merge all dataframes on '2012-12-05' using outer join to keep all keys
df_merged = reduce(lambda left, right: pd.merge(left, right, on='2012-12-05', how='outer'), dfs)

# Convert '2012-12-05' to string type
df_merged['2012-12-05'] = df_merged['2012-12-05'].astype(str)

# Convert '301.0' to numeric integer type (nullable Int64)
df_merged['301.0'] = pd.to_numeric(df_merged['301.0'], errors='coerce').astype('Int64')

# List of float columns to convert
float_cols = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']

for col in float_cols:
    df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').astype(float)

# Group by '2012-12-05' and aggregate:
# sum for '301.0' (integer count-like)
# mean for all float columns
agg_dict = {'301.0': 'sum'}
agg_dict.update({col: 'mean' for col in float_cols})

df_grouped = df_merged.groupby('2012-12-05', as_index=False).agg(agg_dict)

# Ensure column order matches target schema
final_cols = ['2012-12-05', '301.0'] + float_cols
df_grouped = df_grouped[final_cols]

# Write to CSV without index
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)