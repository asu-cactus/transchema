import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("fname", as_index=False).size()
result.columns = ["fname", "count_of_obs"]
result["count_of_obs"] = result["count_of_obs"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)