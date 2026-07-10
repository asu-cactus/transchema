import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)  # batsman, batsman_runs
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)  # batsman, total_runs
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)  # batsman, batsman_runs
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)  # batsman, batsman_runs
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)  # batsman, no of balls, batsman_runs, strike

# Rename batsman_runs columns in df0, df2, df3 to match target schema columns
df0 = df0.rename(columns={'batsman_runs': 'batsman_runs_x'})    # from Source4_35_0
df2 = df2.rename(columns={'batsman_runs': 'batsman_runs_y_6'})  # from Source4_35_2 (6s)
df3 = df3.rename(columns={'batsman_runs': 'batsman_runs_y'})    # from Source4_35_3

# Rename batsman_runs in df4 to batsman_runs_x_4 (4s)
df4 = df4.rename(columns={'batsman_runs': 'batsman_runs_x_4'})

# Join df0 and df2 on batsman
df_merged = pd.merge(df0, df2, on='batsman', how='inner')

# Join the above with df3 on batsman
df_merged = pd.merge(df_merged, df3, on='batsman', how='inner')

# Join with df4 (dimension table with no of balls, strike, batsman_runs_x_4)
df_merged = pd.merge(df_merged, df4, on='batsman', how='inner')

# Join with df1 (total_runs)
df_merged = pd.merge(df_merged, df1, on='batsman', how='inner')

# Group by batsman and aggregate sums and mean strike
agg_df = df_merged.groupby('batsman').agg({
    'batsman_runs_x': 'sum',
    'batsman_runs_y_6': 'sum',
    'batsman_runs_y': 'sum',
    'no of balls': 'sum',
    'batsman_runs_x_4': 'sum',
    'strike': 'mean',
    'total_runs': 'sum'
}).reset_index()

# Ensure correct dtypes as per target schema
agg_df['batsman_runs_x'] = agg_df['batsman_runs_x'].astype(int)
agg_df['batsman_runs_y_6'] = agg_df['batsman_runs_y_6'].astype(int)
agg_df['batsman_runs_y'] = agg_df['batsman_runs_y'].astype(int)
agg_df['no of balls'] = agg_df['no of balls'].astype(int)
agg_df['batsman_runs_x_4'] = agg_df['batsman_runs_x_4'].astype(int)
agg_df['strike'] = agg_df['strike'].astype(float)
agg_df['total_runs'] = agg_df['total_runs'].astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['batsman', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs_x_4', 'strike', 'batsman_runs_y_6', 'total_runs']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)