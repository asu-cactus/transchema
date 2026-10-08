import pandas as pd

# Read source data
source_path = "autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# Group by provider_zip_code and provider_id, aggregate averages by mean
result = df.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Ensure column order matches target schema
result = result[['provider_zip_code', 'provider_id', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)