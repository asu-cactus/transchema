import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

agg = df1.groupby("city").agg(
    fare=("fare", "mean"),
    ride_id=("ride_id", "count")
).reset_index()

driver_sum = df0.groupby("city")["driver_count"].sum().reset_index()

agg = agg.merge(driver_sum, on="city", how="inner")

result = df0.merge(agg, on="city", how="inner")

result = result.rename(columns={
    "fare": "fare",
    "ride_id": "ride_id",
    "driver_count_y": "driver_count",
    "type": "type",
    "city": "city"
})

result = result[["type", "city", "fare", "ride_id", "driver_count"]]

result["ride_id"] = result["ride_id"].astype(float)
result["fare"] = result["fare"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)
result["type"] = result["type"].astype(str)
result["city"] = result["city"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)