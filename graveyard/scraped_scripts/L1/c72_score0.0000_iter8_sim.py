import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("condition", as_index=False)["click"].sum()

result.rename(columns={"click": "0"}, inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)