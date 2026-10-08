import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

# Group by the leftmost non-float columns that uniquely identify providers
group_cols = ['provider_id', 'provider_name', 'provider_zip_code']
agg_cols = ['average_covered_charges', 'average_total_payments', 'average_medicare_payments']

df = df0.groupby(group_cols, as_index=False)[agg_cols].mean()

# Ensure correct dtypes
df['provider_id'] = df['provider_id'].astype(int)
df['provider_zip_code'] = df['provider_zip_code'].astype(int)
df['provider_name'] = df['provider_name'].astype(str)
df['average_covered_charges'] = df['average_covered_charges'].astype(float)
df['average_total_payments'] = df['average_total_payments'].astype(float)
df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)