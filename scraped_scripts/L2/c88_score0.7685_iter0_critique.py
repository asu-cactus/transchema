import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="city", how="inner")

grouped = merged.groupby("city", as_index=False).agg({
    "fare": "mean",
    "ride_id": "count"
})

grouped["fare"] = grouped["fare"].astype(float)
grouped["ride_id"] = grouped["ride_id"].astype(int)
grouped["city"] = grouped["city"].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)