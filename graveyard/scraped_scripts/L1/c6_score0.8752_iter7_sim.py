import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

agg = df0.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'],
    as_index=False
).agg({
    'total_discharges': 'sum',
    'average_covered_charges': 'min',
    'average_total_payments': 'max',
    'average_medicare_payments': 'min'
})

agg = agg.rename(columns={
    'average_covered_charges': 'average_covered_charges',
    'average_total_payments': 'average_total_payments',
    'average_medicare_payments': 'average_medicare_payments'
})

agg['provider_id'] = agg['provider_id'].astype(int)
agg['provider_zip_code'] = agg['provider_zip_code'].astype(int)
agg['provider_name'] = agg['provider_name'].astype(str)
agg['average_covered_charges'] = agg['average_covered_charges'].astype(float)
agg['average_total_payments'] = agg['average_total_payments'].astype(float)
agg['average_medicare_payments'] = agg['average_medicare_payments'].astype(float)

agg = agg[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)