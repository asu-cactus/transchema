import pandas as pd

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_69/test_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_69/test_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_69/test_2.csv', index_col=0)

combined = src0.merge(src1, how='inner', on='user_id').merge(src2, how='inner', on='user_id')
combined.to_csv('autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts_recovery_test_val.csv')