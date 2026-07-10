import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_91/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_91/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_91/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_91/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby("attributes", dropna=True).size().reset_index(name="count")

result = df_grouped[["attributes"]].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_91/target_multisource_mcts.csv", index=False)