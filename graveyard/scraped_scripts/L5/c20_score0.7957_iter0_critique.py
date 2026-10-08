import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_20/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_20/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_20/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_20/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_20/training_4.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert 'state' to categorical codes for counting distinct states
df_all['state'] = df_all['state'].astype('category').cat.codes

# Group by 'longitude' and aggregate
agg_df = df_all.groupby('longitude', as_index=False).agg({
    'missing_count': 'sum',
    'state': pd.Series.nunique,
    'latitude': pd.Series.nunique
})

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'missing_count': 'missing_count',
    'state': 'state',
    'latitude': 'latitude'
})

# Cast columns to correct types
agg_df = agg_df.astype({
    'longitude': float,
    'missing_count': int,
    'state': int,
    'latitude': int
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_20/target_multisource_mcts.csv", index=False)