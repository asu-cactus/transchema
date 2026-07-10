import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_58/training_1.csv", index_col=0)

grouped = df0.groupby("city").agg({"fare": "mean", "ride_id": "max"}).reset_index()

merged = pd.merge(df1, grouped, how="inner", on="city")

result = merged[["type", "fare", "ride_id", "driver_count"]].copy()
result["type"] = result["type"].astype(str)
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_58/target_multisource_mcts.csv", index=False)