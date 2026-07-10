import pandas as pd

# Read both source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

# Join on 'city' column (inner join to keep only matching cities)
df = pd.merge(df0, df1, on='city', how='inner')

# Select only the target columns
df = df[['city', 'fare', 'ride_id']]

# Ensure correct types
df['city'] = df['city'].astype(str)
df['fare'] = df['fare'].astype(float)
df['ride_id'] = pd.to_numeric(df['ride_id'], errors='coerce').fillna(0).astype(int)

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)