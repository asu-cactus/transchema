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

df_all['state'] = df_all['state'].astype('category').cat.codes.astype(int)
df_all['latitude'] = df_all['latitude'].astype(int)

agg_df = df_all.groupby('longitude', as_index=False).agg({
    'missing_count': 'max',
    'state': 'max',
    'latitude': 'max'
})

agg_df = agg_df.astype({
    'longitude': float,
    'missing_count': int,
    'state': int,
    'latitude': int
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_20/target_multisource_mcts.csv", index=False)