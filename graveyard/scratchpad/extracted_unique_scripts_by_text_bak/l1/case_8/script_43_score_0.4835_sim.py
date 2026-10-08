import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

df0['index_track'] = pd.NA
df1['dummy'] = pd.NA

df_union = pd.concat([df0[['index_track', 'track_id', 'dummy']], df1[['index_track', 'track_id', 'dummy']]], ignore_index=True)

df_union['index_track'] = pd.to_numeric(df_union['index_track'], errors='coerce').astype('Int64')
df_union['track_id'] = pd.to_numeric(df_union['track_id'], errors='coerce').astype('Int64')
df_union['dummy'] = pd.to_numeric(df_union['dummy'], errors='coerce').astype('Int64')

df_result = df_union.dropna(subset=['index_track', 'track_id'])
df_result = df_result[['index_track', 'track_id', 'dummy']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)