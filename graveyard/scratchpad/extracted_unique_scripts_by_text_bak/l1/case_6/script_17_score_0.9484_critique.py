import pandas as pd

# Read source table
source_path = "autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# Group by the leftmost non-float unique columns in target schema
group_cols = ['provider_id', 'provider_name', 'provider_zip_code']

# Aggregate mean on the average columns
agg_cols = ['average_covered_charges', 'average_total_payments', 'average_medicare_payments']

result = df.groupby(group_cols, as_index=False)[agg_cols].mean()

# Ensure column order matches target schema exactly
result = result[['provider_id', 'provider_name', 'provider_zip_code',
                 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)