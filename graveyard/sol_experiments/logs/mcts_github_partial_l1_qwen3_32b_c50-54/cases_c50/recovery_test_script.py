import pandas as pd

source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_50/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_50/test_1.csv', index_col=0)

merged = pd.merge(
    source0,
    source1,
    on='calaccess_committee_id',
    how='inner'
)

# Rename columns to match target format
merged = merged.rename(columns={
    'committee_name_x': 'committee_name_x',
    'committee_name_y': 'committee_name_y'
})

merged.to_csv('autopipeline-benchmarks/github-pipelines/length1_50/target_multisource_mcts_recovery_test_val.csv', index=False)