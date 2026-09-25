import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert columns to appropriate types
df_all['month'] = df_all['month'].astype(int)

# Convert 'station' string to integer codes
df_all['station'] = df_all['station'].astype(str)
df_all['station'] = pd.factorize(df_all['station'])[0]

# Convert 'datetime' to integer YYYYMMDD format
df_all['datetime'] = pd.to_datetime(df_all['datetime'], errors='coerce')
df_all['datetime'] = df_all['datetime'].dt.strftime('%Y%m%d').astype(int)

# Convert 'obs_type' string to integer codes
df_all['obs_type'] = df_all['obs_type'].astype(str)
df_all['obs_type'] = pd.factorize(df_all['obs_type'])[0]

# Convert 'TMAX_F' to numeric, fill NaN with 0
df_all['TMAX_F'] = pd.to_numeric(df_all['TMAX_F'], errors='coerce').fillna(0)

# Convert 'country_code' string to integer codes
df_all['country_code'] = df_all['country_code'].astype(str)
df_all['country_code'] = pd.factorize(df_all['country_code'])[0]

# Aggregate: group by month, station, datetime
# Aggregations:
# - obs_value: count
# - obs_type: mean (converted to int later)
# - TMAX_F: mean
# - country_code: mean (converted to int later)
agg_df = df_all.groupby(['month', 'station', 'datetime'], dropna=False).agg(
    obs_value=('obs_value', 'count'),
    obs_type=('obs_type', 'mean'),
    TMAX_F=('TMAX_F', 'mean'),
    country_code=('country_code', 'mean')
).reset_index()

# Convert all columns to int as per target schema
agg_df['month'] = agg_df['month'].astype(int)
agg_df['station'] = agg_df['station'].astype(int)
agg_df['datetime'] = agg_df['datetime'].astype(int)
agg_df['obs_type'] = agg_df['obs_type'].round().astype(int)
agg_df['obs_value'] = agg_df['obs_value'].astype(int)
agg_df['TMAX_F'] = agg_df['TMAX_F'].round().astype(int)
agg_df['country_code'] = agg_df['country_code'].round().astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)