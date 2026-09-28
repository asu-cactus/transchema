import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['TransTo'] = df['TransTo'].fillna(0).astype(int)

result = df.groupby('WarNum', as_index=False)['TransTo'].max()
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)