import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

groupby_result = df0.groupby('user_id', as_index=False).agg({
    'item_id': 'first',
    'rating': 'first',
    'timestamp': 'first'
})

merged = pd.merge(groupby_result, df1[['item_id', 'movie title']], on='item_id', how='inner')

merged = merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

merged['user_id'] = merged['user_id'].astype(int)
merged['item_id'] = merged['item_id'].astype(int)
merged['rating'] = merged['rating'].astype(int)
merged['timestamp'] = merged['timestamp'].astype(int)
merged['movie title'] = merged['movie title'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)