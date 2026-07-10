import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

df0['country_code'] = df0['country_code'].astype(str)
df1['country_code'] = df1['country_code'].astype(str)
df2['country_code'] = df2['country_code'].astype(str)
df3['country_code'] = df3['country_code'].astype(str)

join01 = pd.merge(df0, df1, on=['datetime', 'station', 'obs_type'], suffixes=('_0', '_1'))
join012 = pd.merge(join01, df2, on=['datetime', 'station', 'obs_type'])
join0123 = pd.merge(join012, df3, on=['datetime', 'station', 'obs_type'], suffixes=('', '_3'))

# After join, columns from each source exist, sum numeric columns, pick max country_code lex order (to get one country_code)
# Columns to aggregate: obs_value, TMAX_F from all sources
# month, station, datetime, obs_type are keys for groupby

# Collect obs_value columns
obs_value_cols = [col for col in join0123.columns if col.startswith('obs_value')]
tmax_f_cols = [col for col in join0123.columns if col.startswith('TMAX_F')]
country_code_cols = [col for col in join0123.columns if 'country_code' in col]

group_cols = ['month', 'station', 'datetime', 'obs_type']

# month columns: multiple month columns from different sources, they should be identical per join keys
# To be safe, take the first month column (month_0 or month if no suffix)
month_cols = [col for col in join0123.columns if col.startswith('month')]
# Pick first month column for grouping
month_col = month_cols[0]

# Replace group_cols month with the chosen month_col
group_cols = [month_col if c == 'month' else c for c in group_cols]

agg_dict = {}
for col in obs_value_cols:
    agg_dict[col] = 'sum'
for col in tmax_f_cols:
    agg_dict[col] = 'sum'
for col in country_code_cols:
    agg_dict[col] = 'max'  # max lex order to pick one country_code

grouped = join0123.groupby(group_cols).agg(agg_dict).reset_index()

# Rename columns to target schema
# month, station, datetime, obs_type, obs_value, TMAX_F, country_code
# obs_value and TMAX_F are sums of all sources
grouped['obs_value'] = grouped[obs_value_cols].sum(axis=1)
grouped['TMAX_F'] = grouped[tmax_f_cols].sum(axis=1)
grouped['country_code'] = grouped[country_code_cols].max(axis=1)

result = grouped[[month_col, 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']].copy()
result.rename(columns={month_col: 'month'}, inplace=True)

# Convert month, station, datetime, obs_type, obs_value, TMAX_F to integer if possible
# datetime is string date, convert to integer YYYYMMDD
result['datetime'] = pd.to_datetime(result['datetime'], errors='coerce').dt.strftime('%Y%m%d')
result['datetime'] = pd.to_numeric(result['datetime'], errors='coerce').fillna(0).astype(int)
result['month'] = pd.to_numeric(result['month'], errors='coerce').fillna(0).astype(int)
result['station'] = pd.to_numeric(result['station'], errors='coerce').fillna(0).astype(int)
result['obs_type'] = pd.to_numeric(result['obs_type'], errors='coerce').fillna(0).astype(int)
result['obs_value'] = pd.to_numeric(result['obs_value'], errors='coerce').fillna(0).astype(int)
result['TMAX_F'] = pd.to_numeric(result['TMAX_F'], errors='coerce').fillna(0).astype(int)

# Convert country_code to integer by hashing string consistently
result['country_code'] = result['country_code'].astype(str).apply(lambda x: abs(hash(x)) % (10**9)).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)