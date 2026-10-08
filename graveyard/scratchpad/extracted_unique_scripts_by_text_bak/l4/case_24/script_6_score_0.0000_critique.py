import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_24/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert datetime to integer format YYYYMMDD
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce').dt.strftime('%Y%m%d').astype('Int64')

# Map obs_type to integer codes (consistent across all data)
df['obs_type'] = df['obs_type'].astype('category').cat.codes.astype('Int64')

# Convert numeric columns to Int64 (nullable integer)
df['obs_value'] = pd.to_numeric(df['obs_value'], errors='coerce').astype('Int64')
df['TMAX_F'] = pd.to_numeric(df['TMAX_F'], errors='coerce').astype('Int64')
df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')

# Map country_code to integer codes
country_map = {k: i for i, k in enumerate(sorted(df['country_code'].dropna().unique()))}
df['country_code'] = df['country_code'].map(country_map).astype('Int64')

# Group by the leftmost non-float unique columns in target schema
group_cols = ['station', 'datetime', 'month', 'country_code']

# Aggregate numeric columns by mean (rounded to int)
agg_dict = {
    'obs_type': 'mean',
    'obs_value': 'mean',
    'TMAX_F': 'mean'
}

grouped = df.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

# Round aggregated columns and convert to Int64
for col in ['obs_type', 'obs_value', 'TMAX_F']:
    grouped[col] = grouped[col].round().astype('Int64')

# Reorder columns to match target schema
cols = ['station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month', 'country_code']
grouped = grouped[cols]

# Ensure correct dtypes
grouped = grouped.astype({
    'station': 'string',
    'datetime': 'Int64',
    'obs_type': 'Int64',
    'obs_value': 'Int64',
    'TMAX_F': 'Int64',
    'month': 'Int64',
    'country_code': 'Int64'
})

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_24/target_multisource_mcts.csv", index=False)