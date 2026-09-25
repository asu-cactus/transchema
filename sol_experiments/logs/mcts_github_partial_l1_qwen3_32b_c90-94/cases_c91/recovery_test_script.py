import pandas as pd

# Load the source table
source_path = "autopipeline-benchmarks/github-pipelines/length1_91/test_0.csv"
source_df = pd.read_csv(source_path, index_col=0)

# Ensure column order matches target schema exactly
target_columns = [
    'Name', 'Position', 'Age', 'Team_from', 'League_from',
    'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee'
]
source_df = source_df[target_columns]

# Save to target CSV without index
target_path = "autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts_recovery_test_val.csv"
source_df.to_csv(target_path, index=False)