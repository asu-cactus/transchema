import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_2.csv", index_col=0)

df_union = pd.concat([source1, source2], ignore_index=True, sort=False)

df_unpivot = df_union.melt(id_vars=['user_id', 'movie_id'], value_vars=['gender', 'rating'], var_name='gender_or_rating', value_name='value')

df_f = df_unpivot[df_unpivot['gender_or_rating'] == 'gender'].copy()
df_f = df_f[df_f['value'] == 'F'][['movie_id', 'user_id']]
df_f['F'] = 1

df_m = df_unpivot[df_unpivot['gender_or_rating'] == 'gender'].copy()
df_m = df_m[df_m['value'] == 'M'][['movie_id', 'user_id']]
df_m['M'] = 1

df_rating = df_union[['user_id', 'movie_id', 'rating']]

df_f_ratings = pd.merge(df_f, df_rating, on=['user_id', 'movie_id'], how='left')
df_m_ratings = pd.merge(df_m, df_rating, on=['user_id', 'movie_id'], how='left')

df_f_agg = df_f_ratings.groupby('movie_id')['rating'].mean().reset_index().rename(columns={'rating': 'F'})
df_m_agg = df_m_ratings.groupby('movie_id')['rating'].mean().reset_index().rename(columns={'rating': 'M'})

df_ratings = pd.merge(df_f_agg, df_m_agg, on='movie_id', how='outer')

df_final = pd.merge(df_ratings, source0[['movie_id', 'title']], on='movie_id', how='left')

df_final = df_final[['title', 'F', 'M']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_31/target_multisource_mcts.csv", index=False)