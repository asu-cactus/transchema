import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['station'] = df['station'].astype(str).str.extract('(\d+)$').astype(int)
df['country_code'] = df['country_code'].astype('category').cat.codes

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)

pivot_df = df.pivot_table(index=['month', 'station', 'datetime', 'obs_type', 'obs_value', 'country_code'], 
                          values='TMAX_F', aggfunc='first').reset_index()

pivot_df['TMAX_F'] = pivot_df['TMAX_F'].round().astype(int)

pivot_df = pivot_df[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

pivot_df['obs_type'] = pivot_df['obs_type'].astype('category').cat.codes
pivot_df['obs_value'] = pivot_df['obs_value'].round().astype(int)

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)