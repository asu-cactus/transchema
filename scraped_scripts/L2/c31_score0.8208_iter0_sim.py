import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

grouped = df1.groupby("city").agg({"fare":"mean", "ride_id":"mean"}).reset_index()

merged = pd.merge(df0, grouped, on="city", how="inner")

merged["ride_id"] = merged["ride_id"].astype(float)
merged["fare"] = merged["fare"].astype(float)
merged["driver_count"] = merged["driver_count"].astype(int)
merged["type"] = merged["type"].astype(str)
merged["city"] = merged["city"].astype(str)

result = merged[["type", "city", "fare", "ride_id", "driver_count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)