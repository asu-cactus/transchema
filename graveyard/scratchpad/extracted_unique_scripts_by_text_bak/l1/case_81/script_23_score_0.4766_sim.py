import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# The partial plan suggests a self-join on provider_id and provider_zip_code, which is redundant here.
# Instead, we interpret the plan as a hint to keep these keys and then unpivot the charge/payment columns.

# Select relevant columns
df = df0[['provider_zip_code', 'provider_id', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

# Ensure correct dtypes
df['provider_zip_code'] = pd.to_numeric(df['provider_zip_code'], errors='coerce').astype('Int64')
df['provider_id'] = pd.to_numeric(df['provider_id'], errors='coerce').astype(float)
df['average_covered_charges'] = pd.to_numeric(df['average_covered_charges'], errors='coerce').astype(float)
df['average_total_payments'] = pd.to_numeric(df['average_total_payments'], errors='coerce').astype(float)
df['average_medicare_payments'] = pd.to_numeric(df['average_medicare_payments'], errors='coerce').astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)