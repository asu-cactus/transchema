import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'station' from string to int by extracting trailing digits
df['station'] = df['station'].astype(str).str.extract('(\d+)$').astype(int)

# Convert 'country_code' to categorical codes (int)
df['country_code'] = df['country_code'].astype('category').cat.codes

# Convert 'datetime' to int YYYYMMDD format
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)

# Convert 'obs_type' to categorical codes (int)
df['obs_type'] = df['obs_type'].astype('category').cat.codes

# Round 'obs_value' and convert to int
df['obs_value'] = df['obs_value'].round().astype(int)

# Group by all columns except 'TMAX_F' and aggregate 'TMAX_F' by mean
group_cols = ['month', 'station', 'datetime', 'obs_type', 'obs_value', 'country_code']
agg_df = df.groupby(group_cols, as_index=False)['TMAX_F'].mean()

# Round 'TMAX_F' and convert to int
agg_df['TMAX_F'] = agg_df['TMAX_F'].round().astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)