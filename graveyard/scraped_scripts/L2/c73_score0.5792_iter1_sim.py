import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_73/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

result = merged.rename(columns={"type": "type", "city": "city", "fare": "fare", "ride_id": "ride_id", "driver_count": "driver_count"})

result = result[["type", "city", "fare", "ride_id", "driver_count"]]

result["type"] = result["type"].astype(str)
result["city"] = result["city"].astype(str)
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_73/target_multisource_mcts.csv", index=False)