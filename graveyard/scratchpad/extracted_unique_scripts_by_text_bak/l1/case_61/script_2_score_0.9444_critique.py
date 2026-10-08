import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

df = df0[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']].copy()

# Ensure correct types
df['provider_id'] = df['provider_id'].astype(int)
df['provider_zip_code'] = df['provider_zip_code'].astype(int)
df['provider_name'] = df['provider_name'].astype(str)
df['average_covered_charges'] = df['average_covered_charges'].astype(float)
df['average_total_payments'] = df['average_total_payments'].astype(float)
df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)

# Group by the key columns and aggregate averages by mean
df_grouped = df.groupby(['provider_id', 'provider_name', 'provider_zip_code'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)