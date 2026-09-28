import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("Source Zipcode", as_index=False)["Counts"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)