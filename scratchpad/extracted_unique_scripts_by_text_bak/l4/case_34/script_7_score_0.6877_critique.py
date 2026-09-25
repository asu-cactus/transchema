import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_0.csv", index_col=0)  # batsman, batsman_runs
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_1.csv", index_col=0)  # batsman, total_runs
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_2.csv", index_col=0)  # batsman, no of balls, batsman_runs, strike
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_3.csv", index_col=0)  # batsman, batsman_runs
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_34/training_4.csv", index_col=0)  # batsman, total_runs

# Union batsman_runs tables (s0 and s3) but rename batsman_runs differently to keep separate columns
s0_renamed = s0.rename(columns={'batsman_runs': 'batsman_runs_x'})
s3_renamed = s3.rename(columns={'batsman_runs': 'batsman_runs_y'})

# Since these are separate columns in target, we cannot union them directly.
# Instead, we will join them later on batsman.
# But union means stacking rows, which is not correct here.
# So instead, we keep s0_renamed and s3_renamed separate and join them later.

# Similarly for total_runs tables (s1 and s4)
s1_renamed = s1.rename(columns={'total_runs': 'total_runs_x'})
s4_renamed = s4.rename(columns={'total_runs': 'total_runs_y'})

# Now join s2 with s1_renamed and s4_renamed on batsman to get total_runs_x and total_runs_y
# First join s2 with s1_renamed (total_runs_x)
df = pd.merge(s2, s1_renamed, on='batsman', how='inner')

# Then join with s4_renamed (total_runs_y)
df = pd.merge(df, s4_renamed, on='batsman', how='inner')

# Then join with s0_renamed (batsman_runs_x)
df = pd.merge(df, s0_renamed, on='batsman', how='inner')

# Then join with s3_renamed (batsman_runs_y)
df = pd.merge(df, s3_renamed, on='batsman', how='inner')

# Now df columns:
# batsman, no of balls, batsman_runs (from s2), strike, total_runs_x (from s1), total_runs_y (from s4),
# batsman_runs_x (from s0), batsman_runs_y (from s3)

# Rename s2's batsman_runs to 'batsman_runs' to match target schema
df = df.rename(columns={'batsman_runs': 'batsman_runs'})

# Reorder columns to match target schema:
# ['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']

df = df[['batsman', 'total_runs_x', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs', 'strike', 'total_runs_y']]

# Group by batsman to ensure uniqueness (no aggregation needed as data is already aggregated)
df = df.groupby('batsman', as_index=False).first()

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_34/target_multisource_mcts.csv", index=False)