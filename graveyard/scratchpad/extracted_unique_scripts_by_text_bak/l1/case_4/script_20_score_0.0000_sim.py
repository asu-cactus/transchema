import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby("fname", dropna=False).size().reset_index(name="count_of_obs")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)