import pandas as pd

# Load all source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_0/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_0/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_0/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_0/test_3.csv', index_col=0)

# Execute GROUP_BY operation on des_territ from source3
result = source3.groupby('des_territ', as_index=False).first()

# Save result to target format
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts_recovery_test_val.csv', index=False)