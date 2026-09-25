import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_73/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(df0, df1, on="city", how="inner")

# Group by city and type, aggregate fare by mean
result = joined.groupby(["city", "type"], as_index=False)["fare"].mean()

# Ensure correct types
result["city"] = result["city"].astype(str)
result["type"] = result["type"].astype(str)
result["fare"] = result["fare"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_73/target_multisource_mcts.csv", index=False)