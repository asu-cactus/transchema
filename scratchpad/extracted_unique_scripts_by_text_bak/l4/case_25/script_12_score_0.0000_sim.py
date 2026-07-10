import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_25/training_3.csv", index_col=0)

join_0_1 = pd.merge(df0, df1, on=['datetime', 'station', 'obs_type', 'month', 'country_code'], suffixes=('_0', '_1'))
join_0_1_2 = pd.merge(join_0_1, df2, on=['datetime', 'station', 'obs_type', 'month', 'country_code'])
join_0_1_2_3 = pd.merge(join_0_1_2, df3, on=['datetime', 'station', 'obs_type', 'month', 'country_code'], suffixes=('', '_3'))

# Sum obs_value and TMAX_F columns from all sources
join_0_1_2_3['obs_value'] = (
    join_0_1_2_3['obs_value_0'] + join_0_1_2_3['obs_value_1'] + join_0_1_2_3['obs_value'] + join_0_1_2_3['obs_value_3']
)
join_0_1_2_3['TMAX_F'] = (
    join_0_1_2_3['TMAX_F_0'] + join_0_1_2_3['TMAX_F_1'] + join_0_1_2_3['TMAX_F'] + join_0_1_2_3['TMAX_F_3']
)

result = join_0_1_2_3[['country_code', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'month']]

# Convert datetime to integer format YYYYMMDD
result['datetime'] = pd.to_datetime(result['datetime']).dt.strftime('%Y%m%d').astype(int)

# Convert station and obs_type to integer by factorizing (assigning unique integer codes)
result['station'] = pd.factorize(result['station'])[0]
result['obs_type'] = pd.factorize(result['obs_type'])[0]

# Ensure obs_value, TMAX_F, month are integers (round if needed)
result['obs_value'] = result['obs_value'].round().astype(int)
result['TMAX_F'] = result['TMAX_F'].round().astype(int)
result['month'] = result['month'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_25/target_multisource_mcts.csv", index=False)