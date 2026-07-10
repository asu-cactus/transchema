import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Aggregate df0 by city: count distinct ride_id as driver_count proxy, average fare
agg0 = df0.groupby("city").agg(average_fare=("fare", "mean"), driver_count_approx=("ride_id", "nunique")).reset_index()

# df1 has city, driver_count, type
# Join agg0 with df1 on city to get type and driver_count from df1 (driver_count from df1 preferred)
merged = pd.merge(agg0, df1, on="city", how="inner")

# Use driver_count from df1, average_fare from agg0, city and type from df1
result = merged[["city", "driver_count", "type", "average_fare"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)