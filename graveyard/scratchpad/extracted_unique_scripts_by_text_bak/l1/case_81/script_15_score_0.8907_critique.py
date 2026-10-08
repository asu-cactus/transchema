import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# Group by provider_zip_code (int) and provider_id (float), aggregate payment columns by mean
result = df0.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Cast columns to match target schema types exactly
result['provider_zip_code'] = result['provider_zip_code'].astype(int)
result['provider_id'] = result['provider_id'].astype(float)
result['average_covered_charges'] = result['average_covered_charges'].astype(float)
result['average_total_payments'] = result['average_total_payments'].astype(float)
result['average_medicare_payments'] = result['average_medicare_payments'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)