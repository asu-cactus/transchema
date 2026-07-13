import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_76/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_76/test_1.csv', index_col=0)

merged_df = pd.merge(df0, df1, on='school_name', how='left')

merged_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts_recovery_test_val.csv', index=False)