import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

agg0 = df0.groupby('user_id', as_index=False).agg({'year_school':'count'})
agg2 = df2.groupby('user_id', as_index=False).agg({'fav_music':'count'})

df0_agg = df0.drop_duplicates(subset=['user_id']).copy()
df0_agg = df0_agg[['user_id', 'year_school', 'floor']]

df1_unique = df1.drop_duplicates(subset=['user_id']).copy()
df2_unique = df2.drop_duplicates(subset=['user_id']).copy()

join01 = pd.merge(df0_agg, df1_unique, on='user_id', how='inner')
join012 = pd.merge(join01, df2_unique, on='user_id', how='inner')

join012 = join012.astype({'user_id': 'int64', 'year_school': 'string', 'floor': 'string', 'party': 'string', 'libcon': 'string', 'fav_music': 'string'})

join012.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)