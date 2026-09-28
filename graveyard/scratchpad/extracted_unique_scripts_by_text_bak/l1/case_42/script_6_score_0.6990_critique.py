import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['item_id', 'movie title']], how='inner', on='item_id')

result = merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)