import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv", index_col=0)

# Concatenate (UNION) all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert station to integer by extracting digits
def convert_station(x):
    if isinstance(x, str):
        digits = ''.join(filter(str.isdigit, x))
        return int(digits) if digits else 0
    elif pd.isna(x):
        return 0
    else:
        return int(x)

df['station'] = df['station'].apply(convert_station)

# Convert datetime to integer YYYYMMDD
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d')
df['datetime'] = pd.to_numeric(df['datetime'], errors='coerce').fillna(0).astype(int)

# Convert obs_type to categorical codes (integer)
df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype(int)

# Group by the leftmost columns of target schema
grouped = df.groupby(['country_code', 'station', 'datetime', 'obs_type'], as_index=False).agg({
    'obs_value': 'mean',
    'TMAX_F': 'mean',
    'month': 'mean'
})

# Round aggregated columns and convert to int
grouped['obs_value'] = grouped['obs_value'].round().astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].round().astype(int)
grouped['month'] = grouped['month'].round().astype(int)

# Select and order columns as per target schema
result = grouped[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)