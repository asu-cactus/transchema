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
# Rename batsman_runs to batsman_runs_y_6 as per target schema
src4_renamed = src4.rename(columns={'batsman_runs': 'batsman_runs_y_6'})

# Join all on 'batsman' using inner join to match target row count
df = agg0.merge(agg2, on='batsman', how='inner')
df = df.merge(agg3, on='batsman', how='inner')
df = df.merge(src1_renamed, on='batsman', how='inner')
df = df.merge(src4_renamed[['batsman', 'no of balls', 'strike', 'batsman_runs_y_6']], on='batsman', how='inner')

# Fill NaN with 0 for integer columns where appropriate
int_cols = ['batsman_runs_x', 'batsman_runs_y', 'batsman_runs_x_4', 'total_runs', 'no of balls', 'batsman_runs_y_6']
for col in int_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int)

# strike is float, fill NaN with 0.0
if 'strike' in df.columns:
    df['strike'] = df['strike'].fillna(0.0).astype(float)

# Reorder columns as per target schema
df = df[['batsman', 'batsman_runs_x', 'batsman_runs_y', 'no of balls', 'batsman_runs_x_4', 'strike', 'batsman_runs_y_6', 'total_runs']]

# Save to target CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_35/target_multisource_mcts.csv", index=False)