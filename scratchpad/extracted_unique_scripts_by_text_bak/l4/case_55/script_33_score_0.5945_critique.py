import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df.astype({'WarNum': 'int64', 'WhereFought': 'int64'})

df = df.drop_duplicates(subset=['WarNum', 'WhereFought'])

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)