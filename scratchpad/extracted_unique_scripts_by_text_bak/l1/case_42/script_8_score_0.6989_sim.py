import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['item_id', 'movie title']], on='item_id', how='inner')

grouped = merged.groupby(['movie title', 'user_id'], as_index=False).agg({
    'item_id': 'first',
    'rating': 'first',
    'timestamp': 'first'
})

grouped = grouped.rename(columns={'user_id': 'user_id', 'item_id': 'item_id', 'rating': 'rating', 'timestamp': 'timestamp', 'movie title': 'movie title'})

grouped = grouped[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

grouped['user_id'] = grouped['user_id'].astype(int)
grouped['item_id'] = grouped['item_id'].astype(int)
grouped['rating'] = grouped['rating'].astype(int)
grouped['timestamp'] = grouped['timestamp'].astype(int)
grouped['movie title'] = grouped['movie title'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)