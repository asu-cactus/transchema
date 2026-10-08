import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# Ensure provider_zip_code and provider_id have correct types for grouping
df0['provider_zip_code'] = df0['provider_zip_code'].astype(int)
df0['provider_id'] = df0['provider_id'].astype(float)

agg_df = df0.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Cast columns to target schema types explicitly
agg_df['provider_zip_code'] = agg_df['provider_zip_code'].astype(int)
agg_df['provider_id'] = agg_df['provider_id'].astype(float)
agg_df['average_covered_charges'] = agg_df['average_covered_charges'].astype(float)
agg_df['average_total_payments'] = agg_df['average_total_payments'].astype(float)
agg_df['average_medicare_payments'] = agg_df['average_medicare_payments'].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)