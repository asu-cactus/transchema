import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

agg = df0.groupby(df2.set_index('movie_id').loc[df0['movie_id'], 'title'].values).agg(
    user_id_count=('user_id', 'count'),
    rating_avg=('rating', 'mean'),
    timestamp_min=('timestamp', 'min')
).reset_index().rename(columns={'title': 'title'})

df0_1 = pd.merge(df0, df1, on='user_id', how='inner')
df_merged = pd.merge(df0_1, df2[['movie_id', 'title']], on='movie_id', how='inner')

result = df_merged[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)