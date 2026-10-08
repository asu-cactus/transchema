import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

agg0 = df0.groupby('batsman', as_index=False)['batsman_runs'].sum().rename(columns={'batsman_runs':'batsman_runs_x'})
agg2 = df2.groupby('batsman', as_index=False)['batsman_runs'].sum().rename(columns={'batsman_runs':'batsman_runs_y'})
agg3 = df3.groupby('batsman', as_index=False)['batsman_runs'].sum().rename(columns={'batsman_runs':'batsman_runs_x_4'})

merged = agg0.merge(agg2, on='batsman', how='outer')
merged = merged.merge(agg3, on='batsman', how='outer')
merged = merged.merge(df1, on='batsman', how='outer')
merged = merged.merge(df4, on='batsman', how='outer')

merged['batsman_runs_x'] = merged['batsman_runs_x'].fillna(0).astype(int)
merged['batsman_runs_y'] = merged['batsman_runs_y'].fillna(0).astype(int)
merged['batsman_runs_x_4'] = merged['batsman_runs_x_4'].fillna(0).astype(int)
merged['no of balls'] = merged['no of balls'].fillna(0).astype(int)
merged['strike'] = merged['strike'].astype(float)
merged['batsman_runs_y_6'] = 0
merged['total_runs'] = merged['total_runs'].fillna(0).astype(int)

merged = merged[['batsman', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs_x_4', 'strike', 'batsman_runs_y_6', 'total_runs']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)