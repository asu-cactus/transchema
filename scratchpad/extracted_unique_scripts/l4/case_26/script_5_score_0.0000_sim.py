import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

join_0 = pd.merge(df0, df1, on=["datetime", "station"], suffixes=('_0', '_1'))
join_1 = pd.merge(join_0, df2, on=["datetime", "station"])
join_1 = join_1.rename(columns={col: col + '_2' for col in df2.columns if col not in ['datetime', 'station']})
join_2 = pd.merge(join_1, df3, on=["datetime", "station"])
join_2 = join_2.rename(columns={col: col + '_3' for col in df3.columns if col not in ['datetime', 'station']})

group_cols = [
    'month_0', 'station', 'datetime', 'obs_type_0', 'country_code_0'
]

agg_dict = {
    'obs_value_0': 'count',
    'TMAX_F_0': 'mean',
    'obs_value_1': 'count',
    'TMAX_F_1': 'mean',
    'obs_value_2': 'count',
    'TMAX_F_2': 'mean',
    'obs_value_3': 'count',
    'TMAX_F_3': 'mean'
}

grouped = join_2.groupby(group_cols).agg(agg_dict).reset_index()

# Rename columns to target schema names and convert types
# The target schema is:
# ['month': int, 'station': int, 'datetime': int, 'obs_type': int, 'obs_value': int, 'TMAX_F': int, 'country_code': int]
# The aggregation produces multiple counts and means from 4 sources; the target schema has only one obs_value and TMAX_F.
# We will sum counts and average TMAX_F across sources to produce single obs_value and TMAX_F columns.

grouped['obs_value'] = grouped['obs_value_0'] + grouped['obs_value_1'] + grouped['obs_value_2'] + grouped['obs_value_3']
grouped['TMAX_F'] = grouped[['TMAX_F_0', 'TMAX_F_1', 'TMAX_F_2', 'TMAX_F_3']].mean(axis=1)

# Convert month, station, datetime, obs_type, country_code to integer codes
# First convert to string, then to categorical codes to get integer codes
grouped['month'] = pd.to_numeric(grouped['month_0'], errors='coerce').fillna(0).astype(int)
grouped['station'] = pd.factorize(grouped['station'])[0] + 1
grouped['datetime'] = pd.factorize(grouped['datetime'])[0] + 1
grouped['obs_type'] = pd.factorize(grouped['obs_type_0'])[0] + 1
grouped['country_code'] = pd.factorize(grouped['country_code_0'])[0] + 1

grouped['obs_value'] = grouped['obs_value'].fillna(0).astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].fillna(0).round().astype(int)

result = grouped[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)