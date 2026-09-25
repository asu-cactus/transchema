import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['item_id', 'movie title']], on='item_id', how='inner')

# Select columns in target schema order
result = merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

# Ensure correct types
result['user_id'] = result['user_id'].astype(int)
result['item_id'] = result['item_id'].astype(int)
result['rating'] = result['rating'].astype(int)
result['timestamp'] = result['timestamp'].astype(int)
result['movie title'] = result['movie title'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)