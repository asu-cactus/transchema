import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all['country_code'] = df_all['country_code'].astype(str)
df_all['station'] = df_all['station'].astype(str).str.extract('(\d+)').astype(int)
df_all['datetime'] = pd.to_datetime(df_all['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)
df_all['obs_type'] = df_all['obs_type'].astype('category').cat.codes.astype(int)
df_all['obs_value'] = pd.to_numeric(df_all['obs_value'], errors='coerce').fillna(0).astype(int)
df_all['TMAX_F'] = pd.to_numeric(df_all['TMAX_F'], errors='coerce').fillna(0).astype(int)
df_all['month'] = pd.to_numeric(df_all['month'], errors='coerce').fillna(0).astype(int)

df_all = df_all[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)