import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_24/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_24/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_24/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)
df = df.astype({'condition': int, 'click': int})
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)