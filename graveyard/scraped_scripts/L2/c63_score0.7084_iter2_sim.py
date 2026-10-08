import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

agg_driver = df0.groupby("city", as_index=False)["driver_count"].sum()
agg_fare_ride = df1.groupby("city", as_index=False).agg(fare=("fare", "mean"), ride_id=("ride_id", "count"))

merged = pd.merge(agg_driver, agg_fare_ride, on="city", how="inner")

merged["driver_count"] = merged["driver_count"].astype(int)
merged["fare"] = merged["fare"].astype(float)
merged["ride_id"] = merged["ride_id"].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)