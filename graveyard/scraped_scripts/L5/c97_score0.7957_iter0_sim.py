import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_97/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_97/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_97/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_97/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_97/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

grouped = df_all.groupby("state").agg({
    "missing_count": "sum",
    "latitude": "mean",
    "longitude": "mean"
}).reset_index()

grouped["missing_count"] = grouped["missing_count"].astype(int)
grouped["latitude"] = grouped["latitude"].round().astype(int)
grouped["longitude"] = grouped["longitude"].round().astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_97/target_multisource_mcts.csv", index=False)