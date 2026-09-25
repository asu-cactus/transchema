import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert datetime to integer YYYYMMDD
df_all['datetime'] = pd.to_datetime(df_all['datetime']).dt.strftime('%Y%m%d').astype(int)

# Factorize obs_type to integer codes
df_all['obs_type'] = pd.factorize(df_all['obs_type'])[0]

# Factorize station to integer codes (since target schema expects integer)
df_all['station'] = pd.factorize(df_all['station'])[0]

# Group by country_code, station, datetime
grouped = df_all.groupby(['country_code', 'station', 'datetime'], as_index=False).agg({
    'obs_type': 'first',      # take first obs_type code per group
    'obs_value': 'mean',      # average obs_value per group
    'TMAX_F': 'mean',         # average TMAX_F per group
    'month': 'first'          # month should be consistent per datetime, take first
})

# Round numeric columns to int as target schema expects integers
grouped['obs_value'] = grouped['obs_value'].round().astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].round().astype(int)
grouped['month'] = grouped['month'].astype(int)

# Reorder columns to match target schema exactly
result = grouped[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)