import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_15/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_15/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_15/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_15/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_15/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby('longitude').agg({
    'missing_count': 'mean',
    'state': lambda x: x.astype('category').cat.codes.mean(),
    'latitude': 'mean'
}).reset_index()

agg['missing_count'] = agg['missing_count'].round().astype(int)
agg['state'] = agg['state'].round().astype(int)
agg['latitude'] = agg['latitude'].round().astype(int)

agg = agg[['longitude', 'missing_count', 'state', 'latitude']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_15/target_multisource_mcts.csv", index=False)