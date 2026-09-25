import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_1.csv", index_col=0)

# Join on city
df_joined = pd.merge(df0, df1, on="city", how="inner")

# Group by city and count ride_id
result = df_joined.groupby("city", as_index=False).agg({"ride_id": "count"})

# Ensure ride_id is integer type
result["ride_id"] = result["ride_id"].astype(int)

# Output with exact target schema
result = result[["city", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_5/target_multisource_mcts.csv", index=False)