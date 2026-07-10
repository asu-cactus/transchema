import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city")

result = merged[["type", "city", "fare", "ride_id", "driver_count"]].copy()
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)
result["type"] = result["type"].astype(str)
result["city"] = result["city"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)