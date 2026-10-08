import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_61/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_61/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

result = pd.concat(dfs, ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_61/target_multisource_mcts.csv", index=False)