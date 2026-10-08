import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['state'] = df['state'].astype('category').cat.codes
df['missing_count'] = df['missing_count'].astype(int)
df['latitude'] = df['latitude'].astype(int)
df['longitude'] = df['longitude'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_55/target_multisource_mcts.csv", index=False)