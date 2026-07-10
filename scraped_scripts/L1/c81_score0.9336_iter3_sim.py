import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

df = df0[['provider_zip_code', 'provider_id', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']].copy()

df['provider_zip_code'] = df['provider_zip_code'].astype(int)
df['provider_id'] = df['provider_id'].astype(float)
df['average_covered_charges'] = df['average_covered_charges'].astype(float)
df['average_total_payments'] = df['average_total_payments'].astype(float)
df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)

result = df.groupby('provider_zip_code', as_index=False).agg({
    'provider_id': 'mean',
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)