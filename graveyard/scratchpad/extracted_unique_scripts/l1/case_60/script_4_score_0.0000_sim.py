import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("type", as_index=False)["driver_count"].sum()

result["type"] = result["type"].astype(str)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)