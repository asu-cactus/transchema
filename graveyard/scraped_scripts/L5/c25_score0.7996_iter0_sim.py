import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['state'] = df['state'].astype('category').cat.codes.astype(int)
df['latitude'] = df['latitude'].astype(int)

agg_df = df.groupby('longitude', as_index=False).agg({
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

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_25/target_multisource_mcts.csv", index=False)