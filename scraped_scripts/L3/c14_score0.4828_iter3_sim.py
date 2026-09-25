import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['movie_id', 'title'], value_vars=['genres'], var_name='variable', value_name='genre')
df0_unpivot = df0_unpivot.drop(columns=['variable'])

df_join_1 = pd.merge(df0_unpivot, df1, on='movie_id', how='inner')

df_join_2 = pd.merge(df_join_1, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

result = df_join_2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)