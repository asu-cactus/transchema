import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_6/test_0.csv', index_col=0)
result = df.groupby('provider_id', as_index=False).agg(
    provider_name=('provider_name', 'first'),
    provider_zip_code=('provider_zip_code', 'first'),
    average_covered_charges=('average_covered_charges', 'mean'),
    average_total_payments=('average_total_payments', 'mean'),
    average_medicare_payments=('average_medicare_payments', 'mean')
)
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts_recovery_test_val.csv', index=False)