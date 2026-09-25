import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_1.csv", index_col=0)

# Join on 'city' to keep only rides from cities present in Source2_32_1
joined = pd.merge(df0, df1, on='city', how='inner')

# Select only the target columns and drop duplicates
result = joined[['city', 'ride_id']].drop_duplicates()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_32/target_multisource_mcts.csv", index=False)