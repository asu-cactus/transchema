import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

# Group by the key columns and aggregate averages by mean
result = df.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'], as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Ensure correct dtypes
result['provider_id'] = result['provider_id'].astype(int)
result['provider_zip_code'] = result['provider_zip_code'].astype(int)
result['provider_name'] = result['provider_name'].astype(str)
result['average_covered_charges'] = result['average_covered_charges'].astype(float)
result['average_total_payments'] = result['average_total_payments'].astype(float)
result['average_medicare_payments'] = result['average_medicare_payments'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)