import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

# Join on city
result = pd.merge(df0, df1[['city', 'driver_count']], on='city', how='inner')

# Select only the target columns
result = result[['city', 'driver_count']]

# Remove duplicates if any (should not be needed if city is unique in df1)
result = result.drop_duplicates(subset=['city'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)