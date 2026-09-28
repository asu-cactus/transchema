import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_72/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['state'] = df['state'].astype(str)
df['missing_count'] = df['missing_count'].astype(int)
df['latitude'] = df['latitude'].round().astype(int)
df['longitude'] = df['longitude'].round().astype(int)

df = df[['state', 'missing_count', 'latitude', 'longitude']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_72/target_multisource_mcts.csv", index=False)