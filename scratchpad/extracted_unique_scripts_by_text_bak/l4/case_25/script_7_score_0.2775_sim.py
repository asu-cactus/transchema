import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype('Int64')

df_grouped = df.groupby(
    ['country_code', 'station', 'datetime', 'obs_type', 'month'], dropna=False, observed=False, as_index=False
).agg(
    obs_value=('obs_value', 'mean'),
    TMAX_F=('TMAX_F', 'mean')
)

df_grouped['station'] = df_grouped['station'].astype(str).str.extract('(\d+)').astype('Int64')
df_grouped['obs_type'] = df_grouped['obs_type'].astype(str).str.extract('(\d+)').astype('Int64')
df_grouped['obs_value'] = df_grouped['obs_value'].round().astype('Int64')
df_grouped['TMAX_F'] = df_grouped['TMAX_F'].round().astype('Int64')
df_grouped['month'] = df_grouped['month'].astype('Int64')

df_grouped = df_grouped[
    ['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']
]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)