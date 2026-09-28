import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df['datetime'] = df['datetime'].dt.strftime('%Y%m%d').astype('Int64')

df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype('Int64')
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').astype('Int64')
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').astype('Int64')
df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')

country_map = {k: i for i, k in enumerate(sorted(df['country_code'].dropna().unique()))}
df['country_code'] = df['country_code'].map(country_map).astype('Int64')

pivot_df = df.pivot_table(index=['station', 'datetime', 'month', 'country_code'],
                          columns='obs_type',
                          values='obs_value',
                          aggfunc='first').reset_index()

pivot_df.columns.name = None

pivot_df['obs_type'] = pivot_df['datetime']
pivot_df['obs_value'] = pivot_df['datetime']

pivot_df = pivot_df.rename(columns={'TMAX': 'TMAX_F'})

cols = ['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']
pivot_df = pivot_df.reindex(columns=cols)

pivot_df = pivot_df.astype({
    'station': 'string',
    'datetime': 'Int64',
    'obs_type': 'Int64',
    'obs_value': 'Int64',
    'TMAX_F': 'Int64',
    'month': 'Int64',
    'country_code': 'Int64'
})

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)