import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_5.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

result = union_df[[
    'provider_id',
    'provider_name',
    'provider_zip_code',
    'average_covered_charges',
    'average_total_payments',
    'average_medicare_payments'
]].copy()

result['provider_id'] = result['provider_id'].astype('Int64')
result['provider_name'] = result['provider_name'].astype(str)
result['provider_zip_code'] = result['provider_zip_code'].astype('Int64')
result['average_covered_charges'] = result['average_covered_charges'].astype(float)
result['average_total_payments'] = result['average_total_payments'].astype(float)
result['average_medicare_payments'] = result['average_medicare_payments'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)