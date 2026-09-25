import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

# Join on city
df = pd.merge(df0, df1, on="city", how="inner")

# Group by city and aggregate
agg = df.groupby("city").agg({
    "fare": "mean",
    "ride_id": "count",
    "driver_count": "sum",
    "type": "max"
}).reset_index()

# Rename columns to match target schema
agg = agg.rename(columns={
    "city": "City",
    "fare": "Average Fare ($)",
    "ride_id": "Number of Rides",
    "driver_count": "Number of Drivers",
    "type": "City Type"
})

# Ensure Number of Drivers is integer type
agg["Number of Drivers"] = agg["Number of Drivers"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)