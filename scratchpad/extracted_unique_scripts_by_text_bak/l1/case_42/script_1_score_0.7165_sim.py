import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

df0_pivot = df0.melt(id_vars=['user_id', 'timestamp'], value_vars=['item_id', 'rating'], var_name='variable', value_name='value')
df0_pivot = df0.copy()  # Actually no pivot needed here, partial plan says PIVOT but source0 is already flat, so we interpret PIVOT as no-op or just keep df0 as is.

# The partial plan says PIVOT, but source0 is already in the form user_id, item_id, rating, timestamp.
# So no pivot needed, just rename df0 as pivot_result for plan consistency.
pivot_result = df0

result = pivot_result.merge(df1[['item_id', 'movie title']], on='item_id', how='left')

result = result[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)