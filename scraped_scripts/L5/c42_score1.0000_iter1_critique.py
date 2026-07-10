import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_42/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert missing_count to int (already integer)
df['missing_count'] = df['missing_count'].astype(int)

# Group by missing_count and count non-null values of state, latitude, longitude
agg_df = df.groupby('missing_count').agg({
    'state': 'count',
    'latitude': 'count',
    'longitude': 'count'
}).reset_index()

# Rename columns to match target schema exactly
agg_df.columns = ['missing_count', 'state', 'latitude', 'longitude']

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_42/target_multisource_mcts.csv", index=False)