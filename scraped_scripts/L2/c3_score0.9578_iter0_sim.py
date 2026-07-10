import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_3/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

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

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_3/target_multisource_mcts.csv", index=False)