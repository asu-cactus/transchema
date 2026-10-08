import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

df0 = df0[['provider_zip_code', 'provider_id', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

df0['provider_zip_code'] = pd.to_numeric(df0['provider_zip_code'], errors='coerce').astype('Int64')
df0['provider_id'] = pd.to_numeric(df0['provider_id'], errors='coerce').astype(float)
df0['average_covered_charges'] = pd.to_numeric(df0['average_covered_charges'], errors='coerce').astype(float)
df0['average_total_payments'] = pd.to_numeric(df0['average_total_payments'], errors='coerce').astype(float)
df0['average_medicare_payments'] = pd.to_numeric(df0['average_medicare_payments'], errors='coerce').astype(float)

# Group by provider_zip_code and provider_id, aggregate payment columns by mean
df_grouped = df0.groupby(['provider_zip_code', 'provider_id'], dropna=False, as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)