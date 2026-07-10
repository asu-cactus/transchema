import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby("fac_type", as_index=False)["capacity"].sum()

result["capacity"] = result["capacity"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)