import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

# Group by type, city, ride_id
agg_df = merged.groupby(["type", "city", "ride_id"], as_index=False).agg({
    "fare": "mean",
    "driver_count": "first"
})

# Ensure correct types
agg_df["fare"] = agg_df["fare"].astype(float)
agg_df["ride_id"] = agg_df["ride_id"].astype(float)
agg_df["driver_count"] = agg_df["driver_count"].astype(int)
agg_df["type"] = agg_df["type"].astype(str)
agg_df["city"] = agg_df["city"].astype(str)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)