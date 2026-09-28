import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_35/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby("Source Zipcode", as_index=False)["Counts"].sum()

df_grouped["Source Zipcode"] = df_grouped["Source Zipcode"].astype(int)
df_grouped["Counts"] = df_grouped["Counts"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)