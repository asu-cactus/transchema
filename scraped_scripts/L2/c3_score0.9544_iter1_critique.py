import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df.drop_duplicates()

df['username'] = pd.to_numeric(df['username'], errors='coerce')
df['date'] = df['date'].astype(str)
df['retweets'] = pd.to_numeric(df['retweets'], errors='coerce').fillna(0).astype(int)
df['favorites'] = pd.to_numeric(df['favorites'], errors='coerce').fillna(0).astype(int)
df['text'] = df['text'].astype(str)
df['geo'] = df['geo'].astype(str).replace({'nan': pd.NA})
df['mentions'] = df['mentions'].astype(str).replace({'nan': pd.NA})
df['hashtags'] = df['hashtags'].astype(str).replace({'nan': pd.NA})
df['id'] = pd.to_numeric(df['id'], errors='coerce')
df['permalink'] = df['permalink'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_3/target_multisource_mcts.csv", index=False)