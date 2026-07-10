import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%j').astype('Int64')
    df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype('Int64')
    df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').astype('Int64')
    df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').astype('Int64')
    df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')
    df['country_code'] = df['country_code'].astype('category').cat.codes.astype('Int64')
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

grouped = df_all.groupby('station', dropna=False).agg({
    'datetime': 'count',
    'obs_type': 'count',
    'obs_value': 'count',
    'TMAX_F': 'count',
    'month': 'count',
    'country_code': 'count'
}).reset_index()

grouped.columns = ['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)