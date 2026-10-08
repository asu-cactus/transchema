import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_64/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_64/test_1.csv', index_col=0)

merged_df = pd.merge(source0, source1, left_on='name', right_on='hero_names', how='left')

merged_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_64/target_multisource_mcts_recovery_test_val.csv', index=False)