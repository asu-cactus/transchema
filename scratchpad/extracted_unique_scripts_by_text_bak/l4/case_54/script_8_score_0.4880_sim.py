import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg_df = df_all.groupby("WhereFought", as_index=False).agg(WarNum_min=("WarNum", "min"), WarNum_max=("WarNum", "max"))

min_rows = agg_df[["WhereFought", "WarNum_min"]].rename(columns={"WarNum_min": "WarNum"})
max_rows = agg_df[["WhereFought", "WarNum_max"]].rename(columns={"WarNum_max": "WarNum"})

result = pd.concat([min_rows, max_rows], ignore_index=True).drop_duplicates().sort_values(["WhereFought", "WarNum"]).reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)