import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert datetime to datetime type for formatting
df_all["datetime"] = pd.to_datetime(df_all["datetime"], errors='coerce')

# Group by station (string), datetime (date), obs_type (string), country_code (string)
grouped = df_all.groupby(
    ["station", "datetime", "obs_type", "country_code"],
    as_index=False
).agg({
    "obs_value": "mean",
    "TMAX_F": "mean",
    "month": "mean"
})

# Convert datetime to integer YYYYMMDD format
grouped["datetime"] = grouped["datetime"].dt.strftime("%Y%m%d").astype(int)

# Convert obs_type and country_code to categorical integer codes
grouped["obs_type"] = grouped["obs_type"].astype("category").cat.codes.astype("Int64")
grouped["country_code"] = grouped["country_code"].astype("category").cat.codes.astype("Int64")

# Round and convert aggregated columns to integer type
grouped["obs_value"] = grouped["obs_value"].round().astype("Int64")
grouped["TMAX_F"] = grouped["TMAX_F"].round().astype("Int64")
grouped["month"] = grouped["month"].round().astype("Int64")

# Select columns in target schema order
result = grouped[["station", "datetime", "obs_type", "obs_value", "TMAX_F", "month", "country_code"]]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)