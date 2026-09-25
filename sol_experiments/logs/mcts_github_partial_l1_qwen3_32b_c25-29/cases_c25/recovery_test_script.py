import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_25/test_0.csv', index_col=0)
df0 = df0.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'})

df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_25/test_1.csv', index_col=0)
df1 = df1.rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'})

result = pd.merge(df0, df1, on='State')

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts_recovery_test_val.csv', index=False)