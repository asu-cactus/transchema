import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

df['provider_id'] = pd.to_numeric(df['provider_id'], errors='coerce').astype('Int64')
df['provider_name'] = df['provider_name'].astype(str)
df['provider_zip_code'] = pd.to_numeric(df['provider_zip_code'], errors='coerce').astype('Int64')
df['average_covered_charges'] = pd.to_numeric(df['average_covered_charges'], errors='coerce').astype(float)
df['average_total_payments'] = pd.to_numeric(df['average_total_payments'], errors='coerce').astype(float)
df['average_medicare_payments'] = pd.to_numeric(df['average_medicare_payments'], errors='coerce').astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)