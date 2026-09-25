import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_7.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("Major_category", as_index=False)["Median"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)