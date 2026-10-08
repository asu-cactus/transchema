import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_93/test_0.csv'
df = pd.read_csv(source_path, index_col=0)
df['user_id'] = df['user_id'].str.split(' - ').str[-1]
target_path = 'autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts_recovery_test_val.csv'
df.to_csv(target_path, index=False)