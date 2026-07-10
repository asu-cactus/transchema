import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert 'station' to string
df['station'] = df['station'].astype(str)

# Convert 'datetime' to integer YYYYMMDD format
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d')
df['datetime'] = pd.to_numeric(df['datetime'], errors='coerce').fillna(0).astype(int)

# Factorize 'obs_type' to integer codes
df['obs_type'] = pd.factorize(df['obs_type'].astype(str))[0].astype(int)

# Convert 'month' to integer
df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)

# Factorize 'country_code' to integer codes
df['country_code'] = pd.factorize(df['country_code'].astype(str))[0].astype(int)

# Convert 'obs_value' and 'TMAX_F' to numeric (float) for aggregation
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').fillna(0)
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').fillna(0)

# Group by the key columns and aggregate obs_value and TMAX_F by mean
agg_df = df.groupby(['station', 'datetime', 'obs_type', 'month', 'country_code'], as_index=False).agg({
    'obs_value': 'mean',
    'TMAX_F': 'mean'
})

# Round aggregated columns to int
agg_df['obs_value'] = agg_df['obs_value'].round().astype(int)
agg_df['TMAX_F'] = agg_df['TMAX_F'].round().astype(int)

# Reorder columns to match target schema
agg_df = agg_df[['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)