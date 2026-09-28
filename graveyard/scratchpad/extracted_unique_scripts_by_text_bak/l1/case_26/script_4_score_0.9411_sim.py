import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_26/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

result = merged[["city", "driver_count", "type", "date", "fare", "ride_id"]]

result["driver_count"] = result["driver_count"].astype("Int64")
result["ride_id"] = result["ride_id"].astype("Int64")
result["fare"] = result["fare"].astype(float)
result["date"] = result["date"].astype(str)
result["type"] = result["type"].astype(str)
result["city"] = result["city"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_26/target_multisource_mcts.csv", index=False)