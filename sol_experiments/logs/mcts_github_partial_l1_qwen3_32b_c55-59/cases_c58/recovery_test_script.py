import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_58/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_58/test_1.csv', index_col=0)

source0.rename(columns={'Participation': 'Participation_x'}, inplace=True)
source1.rename(columns={'Participation': 'Participation_y'}, inplace=True)

merged = pd.merge(source0, source1, on='State', how='inner')

merged.to_csv('autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts_recovery_test_val.csv')