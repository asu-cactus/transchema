import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_1.csv", index_col=0)

# Inner join on city to keep only rides in cities present in df0
joined = pd.merge(df1, df0, on="city", how="inner")

# Select only city and ride_id columns as per target schema
result = joined[["city", "ride_id"]]

# Ensure ride_id is integer type as per target schema
result["ride_id"] = result["ride_id"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_75/target_multisource_mcts.csv", index=False)