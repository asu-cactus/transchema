import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv", index_col=0)

# Aggregate df0 by city to get unique driver_count per city (mean in case of duplicates)
df0_agg = df0.groupby("city", as_index=False).agg({"driver_count": "mean"})

# Aggregate df1 by city to get mean fare and ride_id per city
df1_agg = df1.groupby("city", as_index=False).agg({"fare": "mean", "ride_id": "mean"})

# Join aggregated tables on city
merged = pd.merge(df1_agg, df0_agg, on="city", how="inner")

# Select and cast columns as per target schema
result = merged[["city", "fare", "ride_id", "driver_count"]]

result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv", index=False)