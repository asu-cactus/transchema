import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_79/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_79/training_1.csv", index_col=0)

# Aggregate Source2_79_1 by city to get average fare
df1_agg = df1.groupby("city", as_index=False)["fare"].mean()

# Join aggregated fares with Source2_79_0 on city (inner join)
joined = pd.merge(df0, df1_agg, how="inner", on="city")

# Select only city and fare columns as per target schema
result = joined[["city", "fare"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_79/target_multisource_mcts.csv", index=False)