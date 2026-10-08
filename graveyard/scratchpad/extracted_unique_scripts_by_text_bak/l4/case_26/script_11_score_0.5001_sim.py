import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['country_code'] = df['country_code'].astype(str)
    df['station'] = df['station'].astype(str)
    df['obs_type'] = df['obs_type'].astype(str)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all['month'] = pd.to_numeric(df_all['month'], errors='coerce').fillna(0).astype(int)
df_all['station'] = df_all['station'].astype(str)
df_all['obs_type'] = df_all['obs_type'].astype(str)
df_all['country_code'] = df_all['country_code'].astype(str)

df_all['datetime_int'] = df_all['datetime'].dt.strftime('%Y%m%d').astype(int)

df_all['obs_value'] = pd.to_numeric(df_all['obs_value'], errors='coerce').fillna(0)
df_all['TMAX_F'] = pd.to_numeric(df_all['TMAX_F'], errors='coerce').fillna(0)

grouped = df_all.groupby(
    ['month', 'station', 'datetime_int', 'obs_type', 'TMAX_F', 'country_code'],
    dropna=False,
    as_index=False
).agg({'obs_value': 'sum'})

grouped.rename(columns={'datetime_int': 'datetime'}, inplace=True)

grouped['month'] = grouped['month'].astype(int)
grouped['station'] = grouped['station'].astype(str)
grouped['obs_type'] = grouped['obs_type'].astype(str)
grouped['country_code'] = grouped['country_code'].astype(str)
grouped['obs_value'] = grouped['obs_value'].round().astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].round().astype(int)
grouped['datetime'] = grouped['datetime'].astype(int)

grouped = grouped[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)