import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_26/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by 'month' and count rows per month
grouped = df_all.groupby('month').size().reset_index(name='count')

# Prepare the result DataFrame with target schema:
# ['month', 'station', 'datetime', 'obs_type', 'obs_value', 'TMAX_F', 'country_code']
# According to target examples, all columns except month have the same integer value per month (the count)
result = pd.DataFrame({
    'month': grouped['month'].astype(int),
    'station': grouped['count'].astype(int),
    'datetime': grouped['count'].astype(int),
    'obs_type': grouped['count'].astype(int),
    'obs_value': grouped['count'].astype(int),
    'TMAX_F': grouped['count'].astype(int),
    'country_code': grouped['count'].astype(int)
})

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_26/target_multisource_mcts.csv", index=False)