import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_13/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_13/training_1.csv", index_col=0)

# Join on city
df_joined = pd.merge(df0, df1, on="city", how="inner")

# Filter type == 'Urban'
df_filtered = df_joined[df_joined["type"] == "Urban"]

# Group by type and count ride_id
df_agg = df_filtered.groupby("type", as_index=False)["ride_id"].count()

# Rename columns to match target schema
df_agg.rename(columns={"ride_id": "driver_count"}, inplace=True)

# Ensure driver_count is int
df_agg["driver_count"] = df_agg["driver_count"].astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_13/target_multisource_mcts.csv", index=False)