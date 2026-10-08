import pandas as pd

source_0_path = 'autopipeline-benchmarks/github-pipelines/length1_78/test_0.csv'
target_path = 'autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts_recovery_test_val.csv'

df = pd.read_csv(source_0_path, index_col=0)
grouped_df = df.groupby('Product')['Price'].mean().reset_index()
grouped_df.to_csv(target_path, index=False)