import pandas as pd

df_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_0.csv', index_col=0)
df_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_1.csv', index_col=0)
df_2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_2.csv', index_col=0)
df_3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_3.csv', index_col=0)
df_4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_4.csv', index_col=0)
df_5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_5.csv', index_col=0)
df_6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_6.csv', index_col=0)
df_7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_7.csv', index_col=0)
df_8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_8.csv', index_col=0)
df_9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_9.csv', index_col=0)
df_10 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_10.csv', index_col=0)
df_11 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_11.csv', index_col=0)
df_12 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_12.csv', index_col=0)
df_13 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_13.csv', index_col=0)
df_14 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_56/test_14.csv', index_col=0)

combined = pd.concat([
    df_0, df_1, df_2, df_3, df_4, df_5, df_6,
    df_7, df_8, df_9, df_10, df_11, df_12, df_13, df_14
], ignore_index=True)

combined.to_csv(
    'autopipeline-benchmarks/github-pipelines/length9_56/target_multisource_mcts_recovery_test_val.csv',
    index=False
)