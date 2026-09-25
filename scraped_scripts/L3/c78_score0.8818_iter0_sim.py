import pandas as pd

df_ratings = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_0.csv", index_col=0)
df_users = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_1.csv", index_col=0)
df_movies = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_2.csv", index_col=0)

df = df_ratings.merge(df_users[['user_id', 'sex']], on='user_id', how='left')

agg = df.groupby(['movie_id', 'sex'])['rating'].mean().unstack()

agg = agg.rename(columns={'F': 'F', 'M': 'M'})

df_result = df_movies[['movie_id', 'title']].merge(agg, on='movie_id', how='left')

df_result = df_result[['movie_id', 'title', 'F', 'M']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_78/target_multisource_mcts.csv", index=False)