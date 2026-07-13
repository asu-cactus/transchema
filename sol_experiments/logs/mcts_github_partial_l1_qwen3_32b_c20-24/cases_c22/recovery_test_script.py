import pandas as pd

# Load source 0 with index_col=0 to skip the implicit index
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_22/test_0.csv', index_col=0)

# Group by 'condition' and count the number of rows per group
result = src0.groupby('condition')['click'].count().reset_index()

# Save to target CSV with correct column names
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts_recovery_test_val.csv', index=False)