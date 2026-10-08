import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

agg_fare = df1.groupby("city")["fare"].mean().reset_index(name="Average Fare")
agg_ride_count = df1.groupby("city")["ride_id"].nunique().reset_index(name="Total Number of Rides")

df0_agg_driver = df0.groupby(["city", "type"])["driver_count"].max().reset_index(name="Total Number of Drivers")

merged = pd.merge(df0_agg_driver, agg_fare, on="city", how="inner")
merged = pd.merge(merged, agg_ride_count, on="city", how="inner")

merged = merged.rename(columns={
    "city": "City",
    "type": "City Type"
})

merged["ride_id"] = merged["Total Number of Rides"].astype(float)

merged = merged[["City", "Average Fare", "ride_id", "Total Number of Rides", "City Type", "Total Number of Drivers"]]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)