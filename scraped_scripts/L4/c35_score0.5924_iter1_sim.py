import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)

union_df = pd.concat([s0, s2, s3], ignore_index=True)

merged = union_df.merge(s4, on="batsman", how="left", suffixes=('_x', '_y'))

merged = merged.merge(s1, on="batsman", how="left")

merged['batsman_runs_x_4'] = merged['batsman_runs_x'].fillna(0).astype(int)

merged['batsman_runs_y_6'] = merged['batsman_runs_y'].fillna(0).astype(int)

merged['batsman_runs_x'] = merged['batsman_runs_x'].fillna(0).astype(int)

merged['batsman_runs_y'] = merged['batsman_runs_y'].fillna(0).astype(int)

merged['no of balls'] = merged['no of balls'].fillna(0).astype(int)

merged['strike'] = merged['strike'].astype(float)

merged['total_runs'] = merged['total_runs'].fillna(0).astype(int)

result = merged[['batsman', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs_x_4', 'strike', 'batsman_runs_y_6', 'total_runs']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)