import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_0/test_0.csv', index_col=0)
result = df.groupby('State', as_index=False)['AverageTemperature'].mean()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts_recovery_test_val.csv', index=False)