import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

# Convert columns to target schema types
df['username'] = df['username'].astype(float)
df['date'] = df['date'].astype(str)
df['retweets'] = df['retweets'].astype(int)
df['favorites'] = df['favorites'].astype(int)
df['text'] = df['text'].astype(str)
df['geo'] = df['geo'].astype(str)
df['mentions'] = df['mentions'].astype(str)
df['hashtags'] = df['hashtags'].astype(str)
df['id'] = df['id'].astype(float)
df['permalink'] = df['permalink'].astype(str)

# Group by 'permalink' to remove duplicates, take first value for other columns
df = df.groupby('permalink', as_index=False).agg({
    'username': 'first',
    'date': 'first',
    'retweets': 'first',
    'favorites': 'first',
    'text': 'first',
    'geo': 'first',
    'mentions': 'first',
    'hashtags': 'first',
    'id': 'first'
})

# Reorder columns to match target schema exactly
df = df[['username', 'date', 'retweets', 'favorites', 'text', 'geo', 'mentions', 'hashtags', 'id', 'permalink']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_3/target_multisource_mcts.csv", index=False)