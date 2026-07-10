import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['station'] = df['station'].astype(str)
df['country_code'] = df['country_code'].astype(str)

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d')
df['datetime'] = pd.to_numeric(df['datetime'], errors='coerce').fillna(0).astype(int)

df['obs_type'] = pd.to_numeric(df['obs_type'], errors='coerce')
if df['obs_type'].isnull().all():
    # obs_type is string like 'TMAX', convert to integer code by factorizing
    df['obs_type'] = pd.factorize(df['obs_type'].astype(str))[0]
df['obs_type'] = df['obs_type'].fillna(0).astype(int)

df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').fillna(0).astype(int)
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').fillna(0).astype(int)
df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)

# For country_code, convert string codes to integer codes by factorizing
df['country_code'] = pd.factorize(df['country_code'])[0].astype(int)

df = df[['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)