import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

df['provider_id'] = df['provider_id'].astype('Int64')
df['provider_name'] = df['provider_name'].astype(str)
df['provider_zip_code'] = df['provider_zip_code'].astype('Int64')
df['average_covered_charges'] = df['average_covered_charges'].astype(float)
df['average_total_payments'] = df['average_total_payments'].astype(float)
df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)

df = df.groupby(['provider_id', 'provider_name', 'provider_zip_code'], as_index=False).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)