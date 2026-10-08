import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_3.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_4.csv', index_col=0)
df5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_5.csv', index_col=0)
df6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_6.csv', index_col=0)
df7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_7.csv', index_col=0)
df8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_8.csv', index_col=0)
df9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_89/test_9.csv', index_col=0)

result = pd.concat([df0, df1, df2, df3, df4, df5, df6, df7, df8, df9], ignore_index=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_89/target_multisource_mcts_recovery_test_val.csv', index=False)