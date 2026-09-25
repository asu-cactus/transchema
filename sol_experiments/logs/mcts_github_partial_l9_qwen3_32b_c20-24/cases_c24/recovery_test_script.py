import pandas as pd

# Load all source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_0.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_2.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_7.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_1.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_5.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_9.csv', index_col=0)

# Perform initial union of compatible sources (sources 0,2,6,7)
union_table = pd.concat([source0, source2, source6, source7], ignore_index=True)

# Perform all required joins
target_table = union_table.merge(source1, on='ROW_WID', how='left')
target_table = target_table.merge(source3, on='ROW_WID', how='left')
target_table = target_table.merge(source4, on='ROW_WID', how='left')
target_table = target_table.merge(source5, on='ROW_WID', how='left')
target_table = target_table.merge(source8, on='ROW_WID', how='left')
target_table = target_table.merge(source9, on='ROW_WID', how='left')

# Save to CSV
target_table.to_csv('autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts_recovery_test_val.csv', index=False)