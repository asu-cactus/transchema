import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

agg_df1 = df1.groupby("city").agg(
    fare_min=pd.NamedAgg(column="fare", aggfunc="min"),
    fare_max=pd.NamedAgg(column="fare", aggfunc="max"),
    ride_id_sum=pd.NamedAgg(column="ride_id", aggfunc="sum")
).reset_index()

agg_df0 = df0.groupby("city").agg(driver_count_sum=pd.NamedAgg(column="driver_count", aggfunc="sum")).reset_index()

merged = pd.merge(agg_df1, agg_df0, on="city", how="inner")

merged["fare"] = (merged["fare_min"] + merged["fare_max"]) / 2
merged["ride_id"] = merged["ride_id_sum"]
merged["driver_count"] = merged["driver_count_sum"].astype(int)

result = merged[["city", "fare", "ride_id", "driver_count"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)