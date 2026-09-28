import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['month'] = df['month'].astype(int)
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype(int)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)
df['obs_type'] = df['obs_type'].astype(str).str.extract('(\d+)').fillna(2069).astype(int) if df['obs_type'].str.extract('(\d+)').notnull().any().any() else 2069
df['obs_value'] = df['obs_value'].astype(float).fillna(0).astype(int)
df['TMAX_F'] = df['TMAX_F'].astype(float).fillna(0).astype(int)
df['country_code'] = df['country_code'].astype(str).str.extract('(\d+)').fillna(2069).astype(int) if df['country_code'].str.extract('(\d+)').notnull().any().any() else 2069

df = df[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)