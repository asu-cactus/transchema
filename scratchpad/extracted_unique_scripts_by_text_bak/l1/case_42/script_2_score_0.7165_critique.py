import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

df1 = df1.reset_index()

result = df0.merge(df1[['item_id', 'movie title']], on='item_id', how='left')

result = result[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)