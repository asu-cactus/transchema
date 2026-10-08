import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# Group by the leftmost key columns in the target schema
result = df0.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Ensure correct column order and types as per target schema
result = result[['provider_zip_code', 'provider_id', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)