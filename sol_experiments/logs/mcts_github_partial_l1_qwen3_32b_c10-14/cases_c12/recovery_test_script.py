import pandas as pd

# Load source tables
source1_12_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_12/test_0.csv', index_col=0)
source1_12_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_12/test_1.csv', index_col=0)

# Join tables on Athlete column
result = pd.merge(
    source1_12_0,
    source1_12_1,
    on='Athlete',
    how='left'
)

# Save to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts_recovery_test_val.csv', index=False)