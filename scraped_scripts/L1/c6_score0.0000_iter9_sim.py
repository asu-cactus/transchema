import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

agg = df.groupby('provider_id').agg({
    'provider_name': 'first',
    'provider_zip_code': 'first',
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
}).reset_index()

agg['provider_id'] = agg['provider_id'].astype(int)
agg['provider_zip_code'] = agg['provider_zip_code'].astype(int)
agg['provider_name'] = agg['provider_name'].astype(str)
agg['average_covered_charges'] = agg['average_covered_charges'].astype(float)
agg['average_total_payments'] = agg['average_total_payments'].astype(float)
agg['average_medicare_payments'] = agg['average_medicare_payments'].astype(float)

agg = agg[['provider_id', 'provider_name', 'provider_zip_code', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)