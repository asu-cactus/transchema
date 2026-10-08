import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

result = df[['CANCEL_DT']].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)