import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

# Ensure correct dtypes
df0["driver_count"] = pd.to_numeric(df0["driver_count"], errors='coerce').astype("Int64")
df1["fare"] = pd.to_numeric(df1["fare"], errors='coerce')
df1["ride_id"] = pd.to_numeric(df1["ride_id"], errors='coerce')

# Join on city
df_joined = pd.merge(df0, df1, on="city", how="inner")

# Group by city and aggregate
df_grouped = df_joined.groupby("city", as_index=False).agg({
    "fare": "mean",
    "ride_id": "mean",
    "driver_count": "max"
})

# Ensure correct dtypes and column order as target schema
df_grouped["driver_count"] = df_grouped["driver_count"].astype("Int64")
df_grouped = df_grouped[["city", "fare", "ride_id", "driver_count"]]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)