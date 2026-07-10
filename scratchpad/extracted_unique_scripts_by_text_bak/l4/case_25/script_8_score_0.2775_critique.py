import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert datetime to integer YYYYMMDD
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype('Int64')

# Extract digits from station and convert to integer
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype('Int64')

# Convert obs_type to integer by factorizing unique strings
df['obs_type'] = pd.factorize(df['obs_type'])[0].astype('Int64')

# Convert month to integer
df['month'] = df['month'].astype('Int64')

# Group by the leftmost key columns
df_grouped = df.groupby(['country_code', 'station', 'datetime'], dropna=False, as_index=False).agg(
    obs_type=('obs_type', 'count'),
    obs_value=('obs_value', 'count'),
    TMAX_F=('TMAX_F', 'count'),
    month=('month', 'count')
)

# Reorder columns to match target schema
df_grouped = df_grouped[
    ['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']
]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)