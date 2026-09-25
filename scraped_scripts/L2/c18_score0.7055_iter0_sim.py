import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_18/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_18/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city")

grouped = merged.groupby("city").agg({
    "fare": "mean",
    "ride_id": "min"
}).reset_index()

grouped["fare"] = grouped["fare"].astype(float)
grouped["ride_id"] = grouped["ride_id"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_18/target_multisource_mcts.csv", index=False)