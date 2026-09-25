import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

df0 = df0[['track_id', 'dummy']]
df1 = df1[['index_track', 'track_id']]

df0 = df0.assign(index_track=pd.NA)
df1 = df1.assign(dummy=pd.NA)

df = pd.concat([df0, df1], ignore_index=True, sort=False)

df['index_track'] = df['index_track'].astype('Int64')
df['track_id'] = df['track_id'].astype('Int64')
df['dummy'] = df['dummy'].astype('Int64')

df['dummy'] = df['dummy'].fillna(1)
df['index_track'] = df['index_track'].fillna(0).astype(int)

df = df[['index_track', 'track_id', 'dummy']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)