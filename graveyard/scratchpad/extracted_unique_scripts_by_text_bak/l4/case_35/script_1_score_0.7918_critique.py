import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

# Rename batsman_runs columns to match target schema
df0 = df0.rename(columns={'batsman_runs': 'batsman_runs_x'})
df2 = df2.rename(columns={'batsman_runs': 'batsman_runs_y'})
df3 = df3.rename(columns={'batsman_runs': 'batsman_runs_x_4'})
df4 = df4.rename(columns={'batsman_runs': 'batsman_runs_y_6'})

# Join all tables on 'batsman' using outer joins to keep all batsmen
merged = df0.merge(df2, on='batsman', how='outer')
merged = merged.merge(df3, on='batsman', how='outer')
merged = merged.merge(df1, on='batsman', how='outer')
merged = merged.merge(df4, on='batsman', how='outer')

# Fill missing integer columns with 0 and convert to int
for col in ['batsman_runs_x', 'batsman_runs_y', 'batsman_runs_x_4', 'batsman_runs_y_6', 'no of balls', 'total_runs']:
    merged[col] = merged[col].fillna(0).astype(int)

# strike is float, keep as float, fillna if any with NaN (do not fill with 0)
merged['strike'] = merged['strike'].astype(float)

# Reorder columns to match target schema exactly
merged = merged[['batsman', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs_x_4', 'strike', 'batsman_runs_y_6', 'total_runs']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)