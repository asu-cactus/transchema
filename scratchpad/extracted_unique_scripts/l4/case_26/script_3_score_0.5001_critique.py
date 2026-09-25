import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['month'] = df['month'].astype(int)
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype(int)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)
df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype(int)
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').fillna(0).astype(int)
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').fillna(0).astype(int)
df['country_code'] = df['country_code'].astype('category').cat.codes.astype(int)

grouped = df.groupby(['month', 'station', 'datetime', 'obs_type'], as_index=False).agg({
    'obs_value': 'first',
    'TMAX_F': 'first',
    'country_code': 'first'
})

# Reorder columns to match target schema exactly
grouped = grouped[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)