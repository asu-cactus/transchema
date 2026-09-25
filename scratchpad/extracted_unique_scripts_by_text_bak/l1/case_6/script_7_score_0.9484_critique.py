import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

# Group by provider_id, aggregate provider_name and provider_zip_code by first,
# and average the payment columns.
agg_df = df0.groupby('provider_id').agg({
    'provider_name': 'first',
    'provider_zip_code': 'first',
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
}).reset_index()

# Ensure correct dtypes as per target schema
agg_df['provider_id'] = agg_df['provider_id'].astype(int)
agg_df['provider_name'] = agg_df['provider_name'].astype(str)
agg_df['provider_zip_code'] = agg_df['provider_zip_code'].astype(int)
agg_df['average_covered_charges'] = agg_df['average_covered_charges'].astype(float)
agg_df['average_total_payments'] = agg_df['average_total_payments'].astype(float)
agg_df['average_medicare_payments'] = agg_df['average_medicare_payments'].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)