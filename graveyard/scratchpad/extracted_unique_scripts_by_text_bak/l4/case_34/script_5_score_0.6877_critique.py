import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)

# Join total_runs tables (df1 and df4)
join_1 = pd.merge(df1, df4, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join batsman_runs tables (df0 and df3)
join_2 = pd.merge(df0, df3, on="batsman", how="inner", suffixes=('_x', '_y'))

# Join the above two on batsman
join_3 = pd.merge(join_1, join_2, on="batsman", how="inner")

# Join with df2 (which has additional columns)
final_df = pd.merge(join_3, df2, on="batsman", how="inner")

# Rename columns to match target schema exactly
final_df = final_df.rename(columns={
    'total_runs_x': 'total_runs_x',
    'batsman_runs_x': 'batsman_runs_x',
    'batsman_runs_y': 'batsman_runs_y',
    'no of balls': 'no of balls',
    'batsman_runs': 'batsman_runs',
    'strike': 'strike',
    'total_runs_y': 'total_runs_y'
})

# Select columns in target schema order
final_df = final_df[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

# Cast columns to correct types
final_df['total_runs_x'] = final_df['total_runs_x'].astype('Int64')
final_df['batsman_runs_x'] = final_df['batsman_runs_x'].astype('Int64')
final_df['batsman_runs_y'] = final_df['batsman_runs_y'].astype('Int64')
final_df['no of balls'] = final_df['no of balls'].astype('Int64')
final_df['batsman_runs'] = final_df['batsman_runs'].astype('Int64')
final_df['total_runs_y'] = final_df['total_runs_y'].astype('Int64')
final_df['strike'] = final_df['strike'].astype(float)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)