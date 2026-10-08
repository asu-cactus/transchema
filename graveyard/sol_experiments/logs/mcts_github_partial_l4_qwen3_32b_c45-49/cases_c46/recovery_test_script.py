import pandas as pd

# Load sources
source0_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_46/test_0.csv', index_col=0)
source1_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_46/test_1.csv', index_col=0)
source2_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_46/test_2.csv', index_col=0)
source3_df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_46/test_3.csv', index_col=0)

# Add missing columns with defaults
source0_df = source0_df.assign(IsInternational=0, IsIntervention=0)
source1_df = source1_df.assign(IsInternational=0)
source2_df = source2_df.assign(IsInternational=0, IsIntervention=0)
source3_df = source3_df.assign(IsIntervention=0)

# Combine all sources
combined_df = pd.concat([source0_df, source1_df, source2_df, source3_df], ignore_index=True)

# Save to target
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts_recovery_test_val.csv', index=False)