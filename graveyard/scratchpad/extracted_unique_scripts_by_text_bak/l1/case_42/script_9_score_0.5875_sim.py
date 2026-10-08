import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

grouped = df0.groupby(['user_id', 'item_id', 'rating', 'timestamp'], as_index=False).agg({'user_id':'count'})

merged = pd.merge(grouped, df1[['item_id', 'movie title']], how='inner', on='item_id')

result = merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)