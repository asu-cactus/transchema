import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length2_80/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length2_80/training_2.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)
df = df.astype({'0': float, '1': float, '2': float, '3': float})
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)