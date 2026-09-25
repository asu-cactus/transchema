import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_54/test_0.csv', index_col=0)
aggregated = source0.groupby('condition', as_index=False).size().rename(columns={'size': 'click'})
aggregated.to_csv('autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts_recovery_test_val.csv', index=False)