import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_30/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_30/test_1.csv', index_col=0)

joined = pd.merge(source0, source1, on='movieId', how='inner')

joined.to_csv('autopipeline-benchmarks/github-pipelines/length1_30/target_multisource_mcts_recovery_test_val.csv')