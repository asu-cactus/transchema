import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_59/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_59/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby("PRODUCTLINE", as_index=False)["SALES"].sum()

df_grouped["PRODUCTLINE"] = df_grouped["PRODUCTLINE"].astype(str)
df_grouped["SALES"] = df_grouped["SALES"].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)