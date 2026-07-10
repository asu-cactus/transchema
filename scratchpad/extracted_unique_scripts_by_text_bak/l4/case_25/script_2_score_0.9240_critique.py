import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert columns to correct types
df['country_code'] = df['country_code'].astype(str)

# Extract digits from station and convert to int
df['station'] = df['station'].astype(str).str.extract('(\d+)').astype(int)

# Convert datetime to integer format YYYYMMDD
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype(float).fillna(0).astype(int)

# Convert obs_type to categorical codes as int
df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype(int)

# Convert numeric columns to int, filling NaNs with 0
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').fillna(0).astype(int)
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').fillna(0).astype(int)
df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)

# Group by country_code and count rows per country_code
grouped = df.groupby('country_code').agg({
    'station': 'count',
    'datetime': 'count',
    'obs_type': 'count',
    'obs_value': 'count',
    'TMAX_F': 'count',
    'month': 'count'
}).reset_index()

# Rename columns to match target schema
grouped.columns = ['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)