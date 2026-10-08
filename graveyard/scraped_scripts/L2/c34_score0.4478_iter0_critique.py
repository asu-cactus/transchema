import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_1.csv", index_col=0)

# Inner join on city to keep only rides in cities present in df0
joined = pd.merge(df0, df1, on="city", how="inner")

# Select only the target columns
result = joined[["city", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_34/target_multisource_mcts.csv", index=False)