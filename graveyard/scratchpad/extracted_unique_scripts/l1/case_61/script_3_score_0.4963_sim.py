import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

union_result = pd.concat([df0, df1], ignore_index=True)

joined = union_result.merge(union_result, on="provider_id", suffixes=('_left', '_right'))

result = joined[[
    'provider_id',
    'provider_name_left',
    'provider_zip_code_left',
    'average_covered_charges_left',
    'average_total_payments_left',
    'average_medicare_payments_left'
]].copy()

result.columns = [
    'provider_id',
    'provider_name',
    'provider_zip_code',
    'average_covered_charges',
    'average_total_payments',
    'average_medicare_payments'
]

result['provider_id'] = result['provider_id'].astype(int)
result['provider_zip_code'] = result['provider_zip_code'].astype(int)
result['provider_name'] = result['provider_name'].astype(str)
result['average_covered_charges'] = result['average_covered_charges'].astype(float)
result['average_total_payments'] = result['average_total_payments'].astype(float)
result['average_medicare_payments'] = result['average_medicare_payments'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)