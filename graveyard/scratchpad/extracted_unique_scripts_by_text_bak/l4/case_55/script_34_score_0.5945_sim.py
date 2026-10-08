import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_result = df_all.drop_duplicates(subset=["WarNum", "WhereFought"])
df_result = df_result.astype({"WarNum": int, "WhereFought": int})
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)