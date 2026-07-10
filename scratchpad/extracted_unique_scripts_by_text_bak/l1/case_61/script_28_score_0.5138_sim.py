import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

df_target = df0[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']].copy()

df_target['provider_id'] = df_target['provider_id'].astype(int)
df_target['provider_zip_code'] = df_target['provider_zip_code'].astype(int)
df_target['provider_name'] = df_target['provider_name'].astype(str)
df_target['average_covered_charges'] = df_target['average_covered_charges'].astype(float)
df_target['average_total_payments'] = df_target['average_total_payments'].astype(float)
df_target['average_medicare_payments'] = df_target['average_medicare_payments'].astype(float)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)