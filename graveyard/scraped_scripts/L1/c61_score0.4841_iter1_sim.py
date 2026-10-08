import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

df_out = df[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']].copy()

df_out['provider_id'] = df_out['provider_id'].astype(int)
df_out['provider_name'] = df_out['provider_name'].astype(str)
df_out['provider_zip_code'] = df_out['provider_zip_code'].astype(int)
df_out['average_covered_charges'] = df_out['average_covered_charges'].astype(float)
df_out['average_total_payments'] = df_out['average_total_payments'].astype(float)
df_out['average_medicare_payments'] = df_out['average_medicare_payments'].astype(float)

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)