import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert columns to appropriate types
df['month'] = df['month'].astype(int)
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype(int)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)
df['obs_type'] = df['obs_type'].astype(str).str.extract('(\d+)').fillna(0).astype(int)
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').fillna(0).astype(int)
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').fillna(0).astype(int)
df['country_code'] = df['country_code'].astype(str).str.extract('(\d+)').fillna(0).astype(int)

# Group by 'month' and aggregate by count distinct for other columns
agg_df = df.groupby('month').agg({
    'station': pd.Series.nunique,
    'datetime': pd.Series.nunique,
    'obs_type': pd.Series.nunique,
    'obs_value': pd.Series.nunique,
    'TMAX_F': pd.Series.nunique,
    'country_code': pd.Series.nunique
}).reset_index()

# Rename columns to match target schema exactly
agg_df.columns = ['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)