import pandas as pd

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_54/test_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_54/test_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_54/test_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_54/test_3.csv', index_col=0)

combined = pd.concat([src0, src1, src2, src3])
result = combined.groupby('WhereFought', as_index=False).size().rename(columns={'size': 'WarNum'})
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts_recovery_test_val.csv', index=False)