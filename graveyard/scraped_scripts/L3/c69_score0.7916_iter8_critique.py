import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

# Normalize city columns by stripping spaces and lowercasing to ensure matching keys
df0["city"] = df0["city"].str.strip().str.lower()
df1["city"] = df1["city"].str.strip().str.lower()

# Aggregate fare mean by city in df1
agg = df1.groupby("city", as_index=False).agg(fare_mean=("fare", "mean"))

# Join df0 and aggregated df1 on city
joined = pd.merge(df0, agg, how="inner", on="city")

# Select and rename columns to match target schema
result = joined[["city", "type", "fare_mean"]].rename(columns={"fare_mean": "fare"})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)