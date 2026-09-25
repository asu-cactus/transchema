import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv", index_col=0)

# Select relevant columns and ensure correct types
cols = ['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']

df0 = df0[cols].copy()
df1 = df1[cols].copy()
df2 = df2[cols].copy()

# Convert types to match target schema
for df in [df0, df1, df2]:
    df['provider_id'] = df['provider_id'].astype(int)
    df['provider_zip_code'] = df['provider_zip_code'].astype(int)
    df['provider_name'] = df['provider_name'].astype(str)
    df['average_covered_charges'] = df['average_covered_charges'].astype(float)
    df['average_total_payments'] = df['average_total_payments'].astype(float)
    df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)

# UNION all source tables
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# GROUP BY provider_id, provider_name, provider_zip_code and aggregate averages by mean
df_grouped = df_all.groupby(['provider_id', 'provider_name', 'provider_zip_code'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)