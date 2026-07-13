import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_40/test_0.csv', index_col=0)
result = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()
result['QUANTITYORDERED'] = result['QUANTITYORDERED'].astype(int)
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts_recovery_test_val.csv', index=False)