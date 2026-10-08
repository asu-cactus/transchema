import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

union_result = pd.concat([df0, df0], ignore_index=True)

joined = pd.merge(union_result, union_result, on=['provider_id', 'provider_zip_code'], suffixes=('_left', '_right'))

result = pd.DataFrame()
result['provider_zip_code'] = joined['provider_zip_code']
result['provider_id'] = joined['provider_id'].astype(float)
result['average_covered_charges'] = joined['average_covered_charges_left'].astype(float)
result['average_total_payments'] = joined['average_total_payments_left'].astype(float)
result['average_medicare_payments'] = joined['average_medicare_payments_left'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)