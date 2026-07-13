import pandas as pd

source0_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_66/test_0.csv', index_col=0)
source0_df = source0_df.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'})

source1_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_66/test_1.csv', index_col=0)
source1_df = source1_df.rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'})

merged_df = pd.merge(source0_df, source1_df, on='State')

merged_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_66/target_multisource_mcts_recovery_test_val.csv', index=False)