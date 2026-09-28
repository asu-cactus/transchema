import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

grouped = df1.groupby("city").agg({"fare":"mean", "ride_id":"mean"}).reset_index()

merged = pd.merge(df0, grouped, on="city", how="inner")

result = merged[["city", "fare", "ride_id", "driver_count"]]

result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)
result["city"] = result["city"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)