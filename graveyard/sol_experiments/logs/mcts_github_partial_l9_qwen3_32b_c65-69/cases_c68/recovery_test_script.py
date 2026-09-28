import pandas as pd

# Load source tables with index_col=0 to skip first column
source9_68_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_0.csv', index_col=0)
source9_68_2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_2.csv', index_col=0)
source9_68_4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_4.csv', index_col=0)
source9_68_9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_9.csv', index_col=0)

# Union core base tables with identical schema
union_result = pd.concat([source9_68_0, source9_68_2, source9_68_4, source9_68_9], axis=0)

# Load supplemental tables with additional features
source9_68_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_1.csv', index_col=0)  # TECHSUPPORT_NUM
source9_68_3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_3.csv', index_col=0)  # VISITS_NUM
source9_68_5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_5.csv', index_col=0)  # KEYWORDS_NUM
source9_68_6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_6.csv', index_col=0)  # INBOUND_CALLS_NUM
source9_68_7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_7.csv', index_col=0)  # INTERACTIONS_NUM
source9_68_8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/test_8.csv', index_col=0)  # COLLECTION_EVENTS_NUM

# Join all supplemental tables on ROW_WID
for df in [source9_68_1, source9_68_3, source9_68_5, source9_68_6, source9_68_7, source9_68_8]:
    union_result = pd.merge(union_result, df, on='ROW_WID', how='left')

# Save final result to target file
union_result.to_csv('autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts_recovery_test_val.csv')