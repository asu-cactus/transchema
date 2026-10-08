import pandas as pd

# Load source tables
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_14/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_14/test_1.csv', index_col=0)

# Merge with left join to retain all rows from source 0
merged_df = pd.merge(
    left=df0, 
    right=df1, 
    left_on='PLAYER', 
    right_on='Player', 
    how='left'
)

# Save final result with exact column names to file
merged_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_14/target_multisource_mcts_recovery_test_val.csv', index=False)