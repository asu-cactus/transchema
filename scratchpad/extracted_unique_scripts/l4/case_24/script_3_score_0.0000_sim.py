import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype('Int64')
df['obs_type'] = pd.to_numeric(df['obs_type'], errors='coerce').astype('Int64')
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').astype('Int64')
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').astype('Int64')
df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')

country_map = {v: i for i, v in enumerate(sorted(df['country_code'].dropna().unique()), 1)}
df['country_code'] = df['country_code'].map(country_map).astype('Int64')

grouped = df.groupby('station', dropna=False).agg({
    'datetime': 'first',
    'obs_type': 'first',
    'obs_value': 'first',
    'TMAX_F': 'first',
    'month': 'first',
    'country_code': 'first'
}).reset_index()

grouped = grouped.astype({
    'station': 'string',
    'datetime': 'Int64',
    'obs_type': 'Int64',
    'obs_value': 'Int64',
    'TMAX_F': 'Int64',
    'month': 'Int64',
    'country_code': 'Int64'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)