import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/test_0.csv', index_col=0)
grouped = df.groupby('customer_id')['amount'].mean().reset_index()
result = grouped.astype({'customer_id': 'float', 'amount': 'float'})
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts_recovery_test_val.csv', index=False)