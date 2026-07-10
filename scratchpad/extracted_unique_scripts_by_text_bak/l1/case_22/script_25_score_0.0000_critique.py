import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df.astype({'condition': 'int64', 'click': 'int64'})

df = df.groupby('condition', as_index=False).agg({'click': 'sum'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)