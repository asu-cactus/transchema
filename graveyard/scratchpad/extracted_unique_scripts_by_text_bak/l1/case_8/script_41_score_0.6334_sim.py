import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

df0 = df0.copy()
df0['index_track'] = pd.NA
df0 = df0[['index_track', 'track_id', 'dummy']]

df1 = df1.copy()
df1['dummy'] = pd.NA
df1 = df1[['index_track', 'track_id', 'dummy']]

df = pd.concat([df0, df1], ignore_index=True)

df['index_track'] = pd.to_numeric(df['index_track'], errors='coerce').astype('Int64')
df['track_id'] = pd.to_numeric(df['track_id'], errors='coerce').astype('Int64')
df['dummy'] = pd.to_numeric(df['dummy'], errors='coerce').astype('Int64')

df_grouped = df.groupby(['index_track', 'track_id', 'dummy'], dropna=False, as_index=False).size()

df_grouped = df_grouped.rename(columns={'size': 'count'})

df_result = df_grouped[['index_track', 'track_id', 'dummy']]

df_result['dummy'] = df_result['dummy'].fillna(1).astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)