import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_72/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_72/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg_df = df_all.groupby("state", as_index=False).agg({
    "missing_count": "count",
    "latitude": "mean",
    "longitude": "mean"
})

agg_df["missing_count"] = agg_df["missing_count"].astype(int)
agg_df["latitude"] = agg_df["latitude"].round().astype(int)
agg_df["longitude"] = agg_df["longitude"].round().astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_72/target_multisource_mcts.csv", index=False)