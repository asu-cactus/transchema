import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%j').astype(int)

df['obs_type'] = df['obs_type'].astype('category').cat.codes
df['country_code'] = df['country_code'].astype('category').cat.codes
df['station'] = df['station'].astype(str)
df['month'] = df['month'].astype(int)
df['obs_value'] = df['obs_value'].astype(int)
df['TMAX_F'] = df['TMAX_F'].astype(int)
df['datetime'] = df['datetime'].astype(int)

df = df[['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)