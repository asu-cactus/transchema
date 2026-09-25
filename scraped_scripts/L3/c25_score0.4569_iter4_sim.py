import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_2.csv", index_col=0)

agg = df1.groupby(['user_id', 'movie_id'], as_index=False).agg({'rating':'mean', 'timestamp':'max'})
agg.rename(columns={'rating':'rating', 'timestamp':'timestamp'}, inplace=True)

merged_0 = pd.merge(df0, agg, on='user_id', how='inner')
merged_1 = pd.merge(merged_0, df2, on='movie_id', how='inner')

result = merged_1[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_25/target_multisource_mcts.csv", index=False)