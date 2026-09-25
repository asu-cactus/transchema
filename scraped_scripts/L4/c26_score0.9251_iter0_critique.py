import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns according to target schema
df['month'] = df['month'].astype(int)
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype(int)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)
# obs_type is always "TMAX" in examples, encode as 1
df['obs_type'] = 1
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').fillna(0).astype(int)
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').fillna(0).astype(int)
df['country_code'] = df['country_code'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

# Group by month and aggregate counts for all other columns
result = df.groupby('month').agg({
    'station': 'count',
    'datetime': 'count',
    'obs_type': 'count',
    'obs_value': 'count',
    'TMAX_F': 'count',
    'country_code': 'count'
}).reset_index()

# Rename columns to match target schema order
result = result[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)