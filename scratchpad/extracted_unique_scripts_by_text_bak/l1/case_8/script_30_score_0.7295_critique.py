import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# Join on 'track_id' column
df = pd.merge(df1, df0, on='track_id', how='inner')

# Reorder columns to match target schema
df = df[['index_track', 'track_id', 'dummy']]

# Ensure correct dtypes
df['index_track'] = df['index_track'].astype('Int64')
df['track_id'] = df['track_id'].astype('Int64')
df['dummy'] = df['dummy'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)