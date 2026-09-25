import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

agg = df1.groupby("city").agg(
    fare=("fare", "max"),
    ride_id=("ride_id", "count")
).reset_index()

min_driver = df0.groupby("city").agg(driver_count=("driver_count", "min")).reset_index()

agg = agg.merge(min_driver, on="city", how="inner")

result = df0[["city", "type"]].drop_duplicates(subset=["city", "type"])

result = result.merge(agg, on="city", how="inner")

result["ride_id"] = result["ride_id"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)
result["fare"] = result["fare"].astype(float)
result["type"] = result["type"].astype(str)
result["city"] = result["city"].astype(str)

result = result[["type", "city", "fare", "ride_id", "driver_count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)