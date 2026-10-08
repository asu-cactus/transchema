import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

df_join_2_1 = pd.merge(df2, df1[['user_id', 'gender']], on='user_id', how='inner')

df_grouped = df_join_2_1.groupby(['movie_id', 'gender'], as_index=False)['rating'].sum()

df_grouped = pd.merge(df_grouped, df0[['movie_id', 'title']], on='movie_id', how='inner')

df_pivot = df_grouped.pivot(index='title', columns='gender', values='rating').fillna(0)

df_pivot = df_pivot.rename(columns={'F': 'F', 'M': 'M'})

df_pivot = df_pivot.reset_index()

df_pivot = df_pivot[['title', 'F', 'M']]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)