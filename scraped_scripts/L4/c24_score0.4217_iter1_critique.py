import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'datetime' to day of year integer
df['datetime'] = pd.to_datetime(df['datetime']).dt.dayofyear.astype(int)

# Convert categorical columns to codes
df['obs_type'] = df['obs_type'].astype('category').cat.codes
df['country_code'] = df['country_code'].astype('category').cat.codes

# 'station' remains string
df['station'] = df['station'].astype(str)

# 'month' is integer
df['month'] = df['month'].astype(int)

# Aggregate by group
agg_df = df.groupby(['station', 'datetime'], as_index=False).agg({
    'obs_type': 'first',
    'obs_value': 'mean',
    'TMAX_F': 'mean',
    'month': 'first',
    'country_code': 'first'
})

# Convert aggregated numeric columns to int as per target schema
agg_df['obs_value'] = agg_df['obs_value'].round().astype(int)
agg_df['TMAX_F'] = agg_df['TMAX_F'].round().astype(int)
agg_df['obs_type'] = agg_df['obs_type'].astype(int)
agg_df['month'] = agg_df['month'].astype(int)
agg_df['country_code'] = agg_df['country_code'].astype(int)

# Reorder columns to match target schema
agg_df = agg_df[['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)