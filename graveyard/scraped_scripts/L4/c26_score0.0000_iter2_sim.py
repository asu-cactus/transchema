import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

join01 = pd.merge(df0, df1, on=['datetime', 'station', 'obs_type'], suffixes=('_0', '_1'))
join012 = pd.merge(join01, df2, on=['datetime', 'station', 'obs_type'])
join0123 = pd.merge(join012, df3, on=['datetime', 'station', 'obs_type'], suffixes=('', '_3'))

# After join, columns from each source have suffixes or original names:
# We need to aggregate obs_value, TMAX_F from all sources by summing
# For country_code, take max (string max will pick lex max, but we want consistent int)
# But country_code is string in sources, target expects integer, so convert country_code strings to integer codes first

# Convert country_code columns to categorical codes for all sources
for col in ['country_code_0', 'country_code_1', 'country_code', 'country_code_3']:
    if col in join0123.columns:
        join0123[col] = join0123[col].astype('category').cat.codes

# Sum obs_value columns
obs_value_cols = [c for c in join0123.columns if c.startswith('obs_value')]
tmax_f_cols = [c for c in join0123.columns if c.startswith('TMAX_F')]
country_code_cols = [c for c in join0123.columns if c.startswith('country_code')]

join0123['obs_value_sum'] = join0123[obs_value_cols].sum(axis=1)
join0123['TMAX_F_sum'] = join0123[tmax_f_cols].sum(axis=1)
join0123['country_code_max'] = join0123[country_code_cols].max(axis=1)

# month is same in all sources, take from any source
if 'month_0' in join0123.columns:
    join0123['month'] = join0123['month_0']
elif 'month' in join0123.columns:
    join0123['month'] = join0123['month']
else:
    join0123['month'] = join0123['month_1']

# Convert datetime to integer (e.g., timestamp)
join0123['datetime_int'] = pd.to_datetime(join0123['datetime']).astype(int) // 10**9

# Convert station and obs_type to categorical integer codes
join0123['station_int'] = join0123['station'].astype('category').cat.codes
join0123['obs_type_int'] = join0123['obs_type'].astype('category').cat.codes

# Group by month, station_int, datetime_int, obs_type_int and aggregate sums and max
grouped = join0123.groupby(['month', 'station_int', 'datetime_int', 'obs_type_int'], as_index=False).agg({
    'obs_value_sum': 'sum',
    'TMAX_F_sum': 'sum',
    'country_code_max': 'max'
})

# Rename columns to target schema
grouped = grouped.rename(columns={
    'month': 'month',
    'station_int': 'station',
    'datetime_int': 'datetime',
    'obs_type_int': 'obs_type',
    'obs_value_sum': 'obs_value',
    'TMAX_F_sum': 'TMAX_F',
    'country_code_max': 'country_code'
})

# Ensure all columns are integer type as target schema requires
for col in ['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']:
    grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)