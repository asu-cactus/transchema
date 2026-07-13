import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_81/test_0.csv', index_col=0)
grouped = df.groupby('provider_zip_code').agg({
    'provider_id': 'mean',
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
}).reset_index()
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts_recovery_test_val.csv', index=False)