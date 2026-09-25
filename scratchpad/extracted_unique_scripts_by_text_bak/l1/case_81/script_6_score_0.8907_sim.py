import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)

grouped = df_union.groupby(['provider_zip_code', 'provider_id'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_id'] = grouped['provider_id'].astype(float)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

grouped.rename(columns={
    'average_covered_charges': 'average_covered_charges',
    'average_total_payments': 'average_total_payments',
    'average_medicare_payments': 'average_medicare_payments'
}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)