import pandas as pd

# Read source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

# UNION all source tables (concatenate)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY leftmost non-float columns in target schema
group_cols = ['month', 'station', 'datetime', 'obs_type', 'country_code']

# Aggregate: count obs_value, average TMAX_F
agg_dict = {
    'obs_value': 'count',
    'TMAX_F': 'mean'
}

grouped = df_all.groupby(group_cols).agg(agg_dict).reset_index()

# Convert string columns to integer codes as per target schema
# month is integer already, but ensure integer type
grouped['month'] = pd.to_numeric(grouped['month'], errors='coerce').fillna(0).astype(int)

# station, datetime, obs_type, country_code are categorical strings, convert to codes starting at 1
grouped['station'] = pd.factorize(grouped['station'])[0] + 1
grouped['datetime'] = pd.factorize(grouped['datetime'])[0] + 1
grouped['obs_type'] = pd.factorize(grouped['obs_type'])[0] + 1
grouped['country_code'] = pd.factorize(grouped['country_code'])[0] + 1

# Rename aggregated columns to target schema names
grouped = grouped.rename(columns={
    'obs_value': 'obs_value',
    'TMAX_F': 'TMAX_F'
})

# Convert aggregated columns to int as in target schema
grouped['obs_value'] = grouped['obs_value'].fillna(0).astype(int)
grouped['TMAX_F'] = grouped['TMAX_F'].fillna(0).round().astype(int)

# Select columns in target schema order
result = grouped[['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']]

# Write output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)