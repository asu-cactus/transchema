import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_2.csv", index_col=0)

df_0_2 = pd.merge(df0, df2, on="id", suffixes=('_0', '_2'))
df_all = pd.merge(df_0_2, df1, on="id", suffixes=('', '_1'))

# After join, columns from df0, df2, df1 exist with suffixes. We want to produce the target schema:
# ['username': float, 'date': string, 'retweets': integer, 'favorites': integer, 'text': string, 'geo': string, 'mentions': string, 'hashtags': string, 'id': float, 'permalink': string]

# The target examples show username as float (NaN), so keep as is (float NaN).
# For other columns, pick from df0 primarily, if missing, fallback to df1 or df2.

def coalesce_columns(row, cols):
    for c in cols:
        v = row.get(c)
        if pd.notna(v):
            return v
    return pd.NA

result = pd.DataFrame()
result['username'] = df_all.apply(lambda r: coalesce_columns(r, ['username_0', 'username_1', 'username_2']), axis=1).astype(float)
result['date'] = df_all.apply(lambda r: coalesce_columns(r, ['date_0', 'date_1', 'date_2']), axis=1).astype(str)
result['retweets'] = df_all.apply(lambda r: coalesce_columns(r, ['retweets_0', 'retweets_1', 'retweets_2']), axis=1).astype('Int64')
result['favorites'] = df_all.apply(lambda r: coalesce_columns(r, ['favorites_0', 'favorites_1', 'favorites_2']), axis=1).astype('Int64')
result['text'] = df_all.apply(lambda r: coalesce_columns(r, ['text_0', 'text_1', 'text_2']), axis=1).astype(str)
result['geo'] = df_all.apply(lambda r: coalesce_columns(r, ['geo_0', 'geo_1', 'geo_2']), axis=1).astype(str)
result['mentions'] = df_all.apply(lambda r: coalesce_columns(r, ['mentions_0', 'mentions_1', 'mentions_2']), axis=1).astype(str)
result['hashtags'] = df_all.apply(lambda r: coalesce_columns(r, ['hashtags_0', 'hashtags_1', 'hashtags_2']), axis=1).astype(str)
result['id'] = df_all['id'].astype(float)
result['permalink'] = df_all.apply(lambda r: coalesce_columns(r, ['permalink_0', 'permalink_1', 'permalink_2']), axis=1).astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_3/target_multisource_mcts.csv", index=False)