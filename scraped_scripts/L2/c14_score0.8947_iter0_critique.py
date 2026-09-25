import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_14/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

# Convert types as per target schema
df['date'] = df['date'].astype(str)
df['username'] = pd.to_numeric(df['username'], errors='coerce')
df['retweets'] = pd.to_numeric(df['retweets'], errors='coerce').fillna(0).astype(int)
df['favorites'] = pd.to_numeric(df['favorites'], errors='coerce').fillna(0).astype(int)
df['text'] = df['text'].astype(str)

# For geo, mentions, hashtags, replace 'nan' strings with actual NaN
df['geo'] = df['geo'].astype(str).replace({'nan': pd.NA})
df['mentions'] = df['mentions'].astype(str).replace({'nan': pd.NA})
df['hashtags'] = df['hashtags'].astype(str).replace({'nan': pd.NA})

df['id'] = pd.to_numeric(df['id'], errors='coerce')
df['permalink'] = df['permalink'].astype(str)

# Define aggregation functions
agg_dict = {
    'username': 'first',
    'retweets': 'sum',
    'favorites': 'sum',
    'geo': 'first',
    'mentions': 'first',
    'hashtags': 'first',
    'id': 'first'
}

df_grouped = df.groupby(['date', 'text', 'permalink'], dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
df_grouped = df_grouped[['username', 'date', 'retweets', 'favorites', 'text', 'geo', 'mentions', 'hashtags', 'id', 'permalink']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_14/target_multisource_mcts.csv", index=False)