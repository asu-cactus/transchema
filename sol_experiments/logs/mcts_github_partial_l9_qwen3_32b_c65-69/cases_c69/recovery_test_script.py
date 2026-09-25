import pandas as pd

# Load source 0, 1, 3, 4 with union-compatible schema
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_1.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_4.csv', index_col=0)

union_df = pd.concat([source0, source1, source3, source4], axis=0)

# Load and join source2 (KEYWORDS_NUM)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_2.csv', index_col=0)
joined_df = union_df.merge(source2, on='ROW_WID', how='left')

# Load and join source5 (INTERACTIONS_NUM)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_5.csv', index_col=0)
joined_df = joined_df.merge(source5, on='ROW_WID', how='left')

# Load and join source6 (VISITS_NUM)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_6.csv', index_col=0)
joined_df = joined_df.merge(source6, on='ROW_WID', how='left')

# Load and join source7 (COLLECTION_EVENTS_NUM)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_7.csv', index_col=0)
joined_df = joined_df.merge(source7, on='ROW_WID', how='left')

# Load and join source8 (INBOUND_CALLS_NUM)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_8.csv', index_col=0)
joined_df = joined_df.merge(source8, on='ROW_WID', how='left')

# Load and join source9 (TECHSUPPORT_NUM)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/test_9.csv', index_col=0)
joined_df = joined_df.merge(source9, on='ROW_WID', how='left')

# Save final output
joined_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts_recovery_test_val.csv', index=False)