import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

# Join on 'city'
df_merged = pd.merge(df0, df1, on="city", how="inner")

# Group by 'city' and 'driver_count'
# Aggregate fare and ride_id by mean
df_grouped = df_merged.groupby(["city", "driver_count"], as_index=False).agg({
    "fare": "mean",
    "ride_id": "mean"
})

# Ensure correct dtypes
df_grouped["city"] = df_grouped["city"].astype(str)
df_grouped["driver_count"] = pd.to_numeric(df_grouped["driver_count"], errors='coerce').astype("Int64")
df_grouped["fare"] = pd.to_numeric(df_grouped["fare"], errors='coerce').astype(float)
df_grouped["ride_id"] = pd.to_numeric(df_grouped["ride_id"], errors='coerce').astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)