import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_2.csv", index_col=0)

# Join Source1 and Source0 on user_id
df_joined_1 = pd.merge(df1, df0, on='user_id', how='inner')

# Join the above result with Source2 on movie_id
df_joined_2 = pd.merge(df_joined_1, df2[['movie_id']], on='movie_id', how='right')

# Group by movie_id and count ratings (count of non-null rating)
result = df_joined_2.groupby('movie_id')['rating'].count().reset_index(name='0')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)