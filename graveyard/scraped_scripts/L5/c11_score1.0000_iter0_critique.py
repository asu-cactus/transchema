import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_11/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'missing_count' and count the number of rows for 'state', 'latitude', 'longitude'
df_grouped = df_all.groupby('missing_count', as_index=False).agg({
    'state': 'count',
    'latitude': 'count',
    'longitude': 'count'
})

# Rename columns to match target schema exactly
df_grouped.columns = ['missing_count', 'state', 'latitude', 'longitude']

# Convert all columns to int (already int but ensure type)
df_grouped = df_grouped.astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_11/target_multisource_mcts.csv", index=False)