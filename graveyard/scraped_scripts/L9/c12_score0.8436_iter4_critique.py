import pandas as pd
from functools import reduce

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

# Inner join all dataframes on '2012-12-05'
df_merged = reduce(lambda left, right: pd.merge(left, right, on='2012-12-05', how='inner'), dfs)

# Convert '2012-12-05' to string type (date as string)
df_merged['2012-12-05'] = df_merged['2012-12-05'].astype(str)

# Define columns
int_cols = ['301.0']
float_cols = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']

# Convert columns to appropriate types
for col in int_cols:
    if col in df_merged.columns:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').astype('Int64')

for col in float_cols:
    if col in df_merged.columns:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').astype(float)

# Group by '2012-12-05' and aggregate
agg_dict = {}
for col in int_cols:
    agg_dict[col] = 'sum'
for col in float_cols:
    agg_dict[col] = 'mean'

df_final = df_merged.groupby('2012-12-05', as_index=False).agg(agg_dict)

# Reorder columns to match target schema
df_final = df_final[['2012-12-05'] + int_cols + float_cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)