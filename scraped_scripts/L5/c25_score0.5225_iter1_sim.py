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

df['longitude'] = df['longitude'].astype(float)
df['missing_count'] = df['missing_count'].astype(int)
df['state'] = df['state'].astype('category').cat.codes.astype(int)
df['latitude'] = df['latitude'].astype(int)

df = df[['longitude', 'missing_count', 'state', 'latitude']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_25/target_multisource_mcts.csv", index=False)