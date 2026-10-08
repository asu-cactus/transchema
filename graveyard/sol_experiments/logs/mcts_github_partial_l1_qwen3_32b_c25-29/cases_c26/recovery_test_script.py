import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_26/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_26/test_1.csv', index_col=0)

joined = pd.merge(source0, source1, on='city', how='inner')

joined.to_csv('autopipeline-benchmarks/github-pipelines/length1_26/target_multisource_mcts_recovery_test_val.csv', index=False)