import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_97/test_0.csv'
df = pd.read_csv(source_path, index_col=0)
result = df.groupby('crit_cn', as_index=False)['critic'].count()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts_recovery_test_val.csv', index=False)