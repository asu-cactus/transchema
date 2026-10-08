import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby('state', as_index=False).agg({
    'missing_count': 'sum',
    'latitude': 'mean',
    'longitude': 'mean'
})

agg['missing_count'] = agg['missing_count'].astype(int)
agg['state'] = agg['state'].astype('category').cat.codes.astype(int)
agg['latitude'] = agg['latitude'].round().astype(int)
agg['longitude'] = agg['longitude'].round().astype(int)

agg = agg[['missing_count', 'state', 'latitude', 'longitude']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_57/target_multisource_mcts.csv", index=False)