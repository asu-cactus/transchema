import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_52/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

# Convert columns to target schema types
df['username'] = pd.to_numeric(df['username'], errors='coerce')
df['date'] = df['date'].astype(str)
df['retweets'] = pd.to_numeric(df['retweets'], errors='coerce').fillna(0).astype(int)
df['favorites'] = pd.to_numeric(df['favorites'], errors='coerce').fillna(0).astype(int)
df['text'] = df['text'].astype(str)

# For geo, mentions, hashtags: convert 'nan' strings to actual NaN
df['geo'] = df['geo'].astype(str).replace({'nan': pd.NA})
df['mentions'] = df['mentions'].astype(str).replace({'nan': pd.NA})
df['hashtags'] = df['hashtags'].astype(str).replace({'nan': pd.NA})

df['id'] = pd.to_numeric(df['id'], errors='coerce')
df['permalink'] = df['permalink'].astype(str)

df = df[['username', 'date', 'retweets', 'favorites', 'text', 'geo', 'mentions', 'hashtags', 'id', 'permalink']]

# Remove duplicate rows to match target row count
df = df.drop_duplicates(ignore_index=True)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_52/target_multisource_mcts.csv", index=False)