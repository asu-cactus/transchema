import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

# Compute weighted sums for aggregation
df0['covered_charges_total'] = df0['average_covered_charges'] * df0['total_discharges']
df0['total_payments_total'] = df0['average_total_payments'] * df0['total_discharges']
df0['medicare_payments_total'] = df0['average_medicare_payments'] * df0['total_discharges']

# Group by the leftmost key columns of the target schema
grouped = df0.groupby(['provider_id', 'provider_name', 'provider_zip_code'], as_index=False).agg({
    'total_discharges': 'sum',
    'covered_charges_total': 'sum',
    'total_payments_total': 'sum',
    'medicare_payments_total': 'sum'
})

# Compute weighted averages
grouped['average_covered_charges'] = grouped['covered_charges_total'] / grouped['total_discharges']
grouped['average_total_payments'] = grouped['total_payments_total'] / grouped['total_discharges']
grouped['average_medicare_payments'] = grouped['medicare_payments_total'] / grouped['total_discharges']

# Select and reorder columns to match target schema
result = grouped[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

# Cast columns to correct types
result['provider_id'] = result['provider_id'].astype(int)
result['provider_zip_code'] = result['provider_zip_code'].astype(int)
result['provider_name'] = result['provider_name'].astype(str)
result['average_covered_charges'] = result['average_covered_charges'].astype(float)
result['average_total_payments'] = result['average_total_payments'].astype(float)
result['average_medicare_payments'] = result['average_medicare_payments'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)