import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['country_code'] = df['country_code'].astype(str)
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype(int)
df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y%m%d').astype(int)
df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype(int)
df['obs_value'] = df['obs_value'].astype(float).round().astype(int)
df['TMAX_F'] = df['TMAX_F'].astype(float).round().astype(int)
df['month'] = df['month'].astype(int)

df = df[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)