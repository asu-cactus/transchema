import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

pivoted = df.groupby('Gender').size().reset_index(name='0')

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)