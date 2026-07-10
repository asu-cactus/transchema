import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_union = pd.concat(dfs, ignore_index=True)

result = df_union.groupby("condition", as_index=False)["click"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)