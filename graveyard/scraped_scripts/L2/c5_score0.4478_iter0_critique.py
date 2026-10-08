import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_1.csv", index_col=0)

# Join on city (inner join to keep only cities present in both)
joined = pd.merge(df0, df1, on='city', how='inner')

# Select only the target columns
result = joined[['city', 'ride_id']].copy()

# Ensure ride_id is integer type as in target schema
result['ride_id'] = result['ride_id'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_5/target_multisource_mcts.csv", index=False)