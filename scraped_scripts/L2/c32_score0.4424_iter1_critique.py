import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_1.csv", index_col=0)

# Join on 'city' column
df_joined = pd.merge(df0, df1, on='city', how='inner')

# Select only the target columns
df_result = df_joined[['city', 'ride_id']].copy()

# Ensure ride_id is integer type
df_result['ride_id'] = df_result['ride_id'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_32/target_multisource_mcts.csv", index=False)