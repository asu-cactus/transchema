import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_all = df_all.astype({"WarNum": int, "WhereFought": int})
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)