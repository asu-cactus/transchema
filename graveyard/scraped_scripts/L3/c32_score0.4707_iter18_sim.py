import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

df0_sub = df0[['user_id', 'age', 'occupation']]
df1_sub = df1[['user_id', 'movie_id', 'rating', 'timestamp']]

union_result = pd.merge(df0_sub, df1_sub, on='user_id', how='inner')

result = pd.merge(union_result, df2[['movie_id', 'title']], on='movie_id', how='inner')

result = result[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)