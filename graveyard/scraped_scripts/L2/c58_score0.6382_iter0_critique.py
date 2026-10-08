import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_58/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how="inner", on="city")

grouped = merged.groupby("type").agg({
    "fare": "sum",
    "ride_id": "max",
    "driver_count": "sum"
}).reset_index()

result = grouped[["type", "fare", "ride_id", "driver_count"]].copy()

result["type"] = result["type"].astype(str)
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_58/target_multisource_mcts.csv", index=False)