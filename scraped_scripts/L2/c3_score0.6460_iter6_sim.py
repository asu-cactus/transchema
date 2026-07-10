import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_2.csv", index_col=0)

join_result = pd.merge(df0, df2, on="id", suffixes=('_0', '_2'))

id_cols = ['username_0', 'date_0', 'id', 'permalink_0']
value_vars_retweets = ['retweets_0', 'retweets_2']
value_vars_favorites = ['favorites_0', 'favorites_2']
value_vars_text = ['text_0', 'text_2']
value_vars_geo = ['geo_0', 'geo_2']
value_vars_mentions = ['mentions_0', 'mentions_2']
value_vars_hashtags = ['hashtags_0', 'hashtags_2']

df_retweets = join_result.melt(id_vars=id_cols, value_vars=value_vars_retweets, var_name='var', value_name='retweets')
df_favorites = join_result.melt(id_vars=id_cols, value_vars=value_vars_favorites, var_name='var', value_name='favorites')
df_text = join_result.melt(id_vars=id_cols, value_vars=value_vars_text, var_name='var', value_name='text')
df_geo = join_result.melt(id_vars=id_cols, value_vars=value_vars_geo, var_name='var', value_name='geo')
df_mentions = join_result.melt(id_vars=id_cols, value_vars=value_vars_mentions, var_name='var', value_name='mentions')
df_hashtags = join_result.melt(id_vars=id_cols, value_vars=value_vars_hashtags, var_name='var', value_name='hashtags')

df_unpivot = df_retweets[['username_0','date_0','id','permalink_0','retweets']].copy()
df_unpivot['favorites'] = df_favorites['favorites']
df_unpivot['text'] = df_text['text']
df_unpivot['geo'] = df_geo['geo']
df_unpivot['mentions'] = df_mentions['mentions']
df_unpivot['hashtags'] = df_hashtags['hashtags']

df_unpivot.rename(columns={
    'username_0': 'username',
    'date_0': 'date',
    'permalink_0': 'permalink'
}, inplace=True)

df_unpivot['username'] = df_unpivot['username'].astype(float)
df_unpivot['id'] = df_unpivot['id'].astype(float)
df_unpivot['date'] = df_unpivot['date'].astype(str)
df_unpivot['retweets'] = df_unpivot['retweets'].astype(int)
df_unpivot['favorites'] = df_unpivot['favorites'].astype(int)
df_unpivot['text'] = df_unpivot['text'].astype(str)
df_unpivot['geo'] = df_unpivot['geo'].astype(str)
df_unpivot['mentions'] = df_unpivot['mentions'].astype(str)
df_unpivot['hashtags'] = df_unpivot['hashtags'].astype(str)
df_unpivot['permalink'] = df_unpivot['permalink'].astype(str)

df1['username'] = df1['username'].astype(float)
df1['id'] = df1['id'].astype(float)
df1['date'] = df1['date'].astype(str)
df1['retweets'] = df1['retweets'].astype(int)
df1['favorites'] = df1['favorites'].astype(int)
df1['text'] = df1['text'].astype(str)
df1['geo'] = df1['geo'].astype(str)
df1['mentions'] = df1['mentions'].astype(str)
df1['hashtags'] = df1['hashtags'].astype(str)
df1['permalink'] = df1['permalink'].astype(str)

final_df = pd.concat([df_unpivot, df1], ignore_index=True)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_3/target_multisource_mcts.csv", index=False)