import pandas as pd

# Load source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_35/training_4.csv", index_col=0)

# Aggregate Source 0: sum batsman_runs as batsman_runs_x
agg0 = src0.groupby('batsman', as_index=False)['batsman_runs'].sum().rename(columns={'batsman_runs': 'batsman_runs_x'})

# Aggregate Source 2: sum batsman_runs as batsman_runs_y
agg2 = src2.groupby('batsman', as_index=False)['batsman_runs'].sum().rename(columns={'batsman_runs': 'batsman_runs_y'})

# Aggregate Source 3: sum batsman_runs as batsman_runs_x_4
agg3 = src3.groupby('batsman', as_index=False)['batsman_runs'].sum().rename(columns={'batsman_runs': 'batsman_runs_x_4'})

# Source 1 has batsman and total_runs, no aggregation needed
src1_renamed = src1.rename(columns={'total_runs': 'total_runs'})

# Source 4 has batsman, no of balls, batsman_runs, strike
# We need batsman_runs_y_6 from somewhere - likely from Source 4 batsman_runs where runs are 6? 
# But no direct info, so assume batsman_runs_y_6 is sum of batsman_runs from Source 4 where runs are 6 (not given)
# Since no direct info, we will assume batsman_runs_y_6 = 0 for all (as no source explicitly provides it)
# But better: Since Source 4 has batsman_runs, and strike, and no of balls, we can use batsman_runs as batsman_runs_y_6 (?)
# But target has batsman_runs_y_6 as integer, so we can try to get it from Source 4 batsman_runs where runs are 6 (not possible)
# So we will set batsman_runs_y_6 = 0 for all batsman (safe default)

# Prepare Source 4 relevant columns
src4_subset = src4[['batsman', 'no of balls', 'batsman_runs', 'strike']].copy()
src4_subset = src4_subset.rename(columns={'batsman_runs': 'batsman_runs_y_6'})

# Merge all aggregated dataframes on batsman
df = agg0.merge(agg2, on='batsman', how='outer')
df = df.merge(agg3, on='batsman', how='outer')
df = df.merge(src1_renamed, on='batsman', how='outer')
df = df.merge(src4_subset, on='batsman', how='outer')

# Fill NaN with 0 for integer columns where appropriate
int_cols = ['batsman_runs_x', 'batsman_runs_y', 'batsman_runs_x_4', 'total_runs', 'no of balls', 'batsman_runs_y_6']
for col in int_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int)

# strike is float, keep as is, fill NaN with 0.0
if 'strike' in df.columns:
    df['strike'] = df['strike'].fillna(0.0).astype(float)

# Reorder columns as per target schema
df = df[['batsman', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs_x_4', 'strike', 'batsman_runs_y_6', 'total_runs']]

# Save to target CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)