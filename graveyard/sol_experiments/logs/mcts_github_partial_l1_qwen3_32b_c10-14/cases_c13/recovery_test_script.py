import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/test_0.csv', index_col=0)
result = df.groupby(['sex', 'smoker'])['tip_pct'].mean().reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts_recovery_test_val.csv', index=True)