import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['month'] = df_all['month'].astype(int)
df_all['station'] = df_all['station'].astype(str)
df_all['datetime'] = pd.to_datetime(df_all['datetime'], errors='coerce')
df_all['datetime'] = df_all['datetime'].dt.strftime('%Y%m%d').astype(int)
df_all['obs_type'] = df_all['obs_type'].astype(str)
df_all['TMAX_F'] = pd.to_numeric(df_all['TMAX_F'], errors='coerce').fillna(0).astype(int)
df_all['country_code'] = df_all['country_code'].astype(str)

grouped = df_all.groupby(['month', 'station', 'datetime', 'obs_type', 'TMAX_F', 'country_code'], dropna=False).agg(obs_value=('obs_value', 'count')).reset_index()

grouped['month'] = grouped['month'].astype(int)
grouped['station'] = grouped['station'].astype(int, errors='ignore')
grouped['datetime'] = grouped['datetime'].astype(int)
grouped['obs_type'] = grouped['obs_type'].astype(int, errors='ignore')
grouped['obs_value'] = grouped['obs_value'].astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].astype(int)
grouped['country_code'] = grouped['country_code'].astype(int, errors='ignore')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)