import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

df0_sub = df0[['user_id', 'age', 'occupation']]
df1_sub = df1[['user_id', 'movie_id', 'rating', 'timestamp']]

df01 = pd.merge(df1_sub, df0_sub, on='user_id', how='left')

df_final = pd.merge(df01, df2[['movie_id', 'title']], on='movie_id', how='left')

df_final = df_final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

df_final['user_id'] = df_final['user_id'].astype(float)
df_final['movie_id'] = df_final['movie_id'].astype(int)
df_final['rating'] = df_final['rating'].astype(float)
df_final['timestamp'] = df_final['timestamp'].astype(float)
df_final['age'] = df_final['age'].astype(float)
df_final['occupation'] = df_final['occupation'].astype(float)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)