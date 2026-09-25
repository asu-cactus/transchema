import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['station'] = df['station'].str.extract('(\d+)').astype(int)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype('Int64')
df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype('Int64')
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').astype('Int64')
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').astype('Int64')
df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')
df['country_code'] = df['country_code'].astype(str)

df = df[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)