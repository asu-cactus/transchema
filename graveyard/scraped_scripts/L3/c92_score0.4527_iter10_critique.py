import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
joined_0 = pd.merge(df2, df0, how='inner', on='movie_id')

# Join the above with users on user_id
joined_1 = pd.merge(joined_0, df1, how='inner', on='user_id')

result = pd.DataFrame()
result['title'] = joined_1['title']
result['movie_id'] = joined_1['movie_id']
result['video_release_date'] = pd.to_numeric(joined_1['video_release_date'], errors='coerce')
result['user_id'] = joined_1['user_id'].astype(float)
result['rating'] = joined_1['rating'].astype(float)
result['unix_timestamp'] = joined_1['unix_timestamp'].astype(float)
result['age'] = joined_1['age'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)