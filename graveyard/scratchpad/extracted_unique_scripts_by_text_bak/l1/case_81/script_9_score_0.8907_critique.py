import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# Convert provider_zip_code to integer, provider_id to float
df0['provider_zip_code'] = pd.to_numeric(df0['provider_zip_code'], errors='coerce').astype('Int64')
df0['provider_id'] = pd.to_numeric(df0['provider_id'], errors='coerce').astype(float)

# Drop rows with missing provider_zip_code or provider_id to avoid losing rows in groupby
df0 = df0.dropna(subset=['provider_zip_code', 'provider_id'])

# Group by provider_zip_code and provider_id, aggregate averages
grouped = df0.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Ensure correct types as per target schema
grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_id'] = grouped['provider_id'].astype(float)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)