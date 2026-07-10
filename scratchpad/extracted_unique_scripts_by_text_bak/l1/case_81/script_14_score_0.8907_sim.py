import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# The partial plan suggests a self-join on provider_id and provider_zip_code, but joining the same table to itself on identical keys without additional tables or columns is redundant.
# Instead, we interpret the plan as grouping by provider_zip_code and provider_id and averaging the relevant columns.

grouped = df0.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Rename columns to match target schema
grouped = grouped.rename(columns={
    'average_covered_charges': 'average_covered_charges',
    'average_total_payments': 'average_total_payments',
    'average_medicare_payments': 'average_medicare_payments',
    'provider_zip_code': 'provider_zip_code',
    'provider_id': 'provider_id'
})

# Ensure data types match target schema
grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_id'] = grouped['provider_id'].astype(float)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)