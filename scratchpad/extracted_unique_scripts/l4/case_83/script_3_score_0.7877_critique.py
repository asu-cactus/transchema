import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(df0, df1, on="city", how="inner")

# Group by city, driver_count, type and aggregate average fare
grouped = merged.groupby(["city", "driver_count", "type"], as_index=False).agg(average_fare=("fare", "mean"))

# Ensure correct dtypes as per target schema
grouped["city"] = grouped["city"].astype(str)
grouped["driver_count"] = grouped["driver_count"].astype(int)
grouped["type"] = grouped["type"].astype(str)
grouped["average_fare"] = grouped["average_fare"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)