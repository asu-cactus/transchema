import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_20/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_20/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_20/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_20/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length3_20/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

grouped = df_all.groupby("SN", as_index=False)["Price"].mean()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_20/target_multisource_mcts.csv", index=False)