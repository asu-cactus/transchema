import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['month'] = df_all['month'].astype(int)
df_all['station'] = df_all['station'].astype(str)
df_all['datetime'] = df_all['datetime'].astype(str)
df_all['obs_type'] = df_all['obs_type'].astype(str)
df_all['country_code'] = df_all['country_code'].astype(str)

grouped = df_all.groupby(['month', 'station', 'datetime', 'obs_type', 'country_code'], dropna=False).agg({
    'obs_value': 'mean',
    'TMAX_F': 'mean'
}).reset_index()

grouped['month'] = grouped['month'].astype(int)
grouped['station'] = grouped['station'].astype(int, errors='ignore') if grouped['station'].str.isnumeric().all() else grouped['station']
grouped['datetime'] = grouped['datetime'].astype(int, errors='ignore') if grouped['datetime'].str.isnumeric().all() else grouped['datetime']
grouped['obs_type'] = grouped['obs_type'].astype(int, errors='ignore') if grouped['obs_type'].str.isnumeric().all() else grouped['obs_type']
grouped['country_code'] = grouped['country_code'].astype(int, errors='ignore') if grouped['country_code'].str.isnumeric().all() else grouped['country_code']

grouped['obs_value'] = grouped['obs_value'].round().astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].round().astype(int)

grouped = grouped.rename(columns={
    'obs_value': 'obs_value',
    'TMAX_F': 'TMAX_F'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)