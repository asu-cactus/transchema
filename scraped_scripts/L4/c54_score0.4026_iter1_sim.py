import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)
df = df[['WhereFought', 'WarNum']]
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)