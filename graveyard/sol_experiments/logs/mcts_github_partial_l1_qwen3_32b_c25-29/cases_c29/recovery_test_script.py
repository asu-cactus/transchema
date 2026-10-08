import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_29/test_0.csv', index_col=0)
result = df.groupby('Gender').size().reset_index(name='0')
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts_recovery_test_val.csv', index=False)