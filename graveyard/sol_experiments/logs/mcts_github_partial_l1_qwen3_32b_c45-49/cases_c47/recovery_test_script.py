import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_47/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_47/test_1.csv', index_col=0)

joined = pd.merge(source0, source1, on='school_name')

joined.to_csv('autopipeline-benchmarks/github-pipelines/length1_47/target_multisource_mcts_recovery_test_val.csv')