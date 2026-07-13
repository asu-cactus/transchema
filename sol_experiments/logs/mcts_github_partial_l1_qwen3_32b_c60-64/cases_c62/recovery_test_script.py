import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_62/test_0.csv', index_col=0)
result = df.groupby('Text Date')[['Water Use', 'Power Use']].sum().reset_index()
result.rename(columns={'Text Date': 'Month'}, inplace=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts_recovery_test_val.csv', index=False)