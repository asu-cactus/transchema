import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_85/test_0.csv', index_col=0)
result = source0.groupby('crit_cn')['critic'].count().reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts_recovery_test_val.csv', index=False)