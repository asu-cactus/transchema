import pandas as pd

# Load source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_88/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_88/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_88/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_88/test_3.csv', index_col=0)

# Union sources and deduplicate TrackIDs via grouping
combined = pd.concat([source0, source1, source2, source3], ignore_index=True)
result = combined.groupby('TrackID', as_index=False).first()[['TrackID']]

# Save to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts_recovery_test_val.csv', index=False)