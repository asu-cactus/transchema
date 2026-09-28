import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

df_grouped = df.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'], as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

df_grouped['provider_id'] = df_grouped['provider_id'].astype(int)
df_grouped['provider_zip_code'] = df_grouped['provider_zip_code'].astype(int)
df_grouped['provider_name'] = df_grouped['provider_name'].astype(str)
df_grouped['average_covered_charges'] = df_grouped['average_covered_charges'].astype(float)
df_grouped['average_total_payments'] = df_grouped['average_total_payments'].astype(float)
df_grouped['average_medicare_payments'] = df_grouped['average_medicare_payments'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)