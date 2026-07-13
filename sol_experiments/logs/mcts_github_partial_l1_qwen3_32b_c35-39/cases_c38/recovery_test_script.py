import pandas as pd

# Define source file path
src_path = 'autopipeline-benchmarks/github-pipelines/length1_38/test_0.csv'

# Load source data
df = pd.read_csv(src_path, index_col=0)

# Group by user_id and calculate mean values
result = df.groupby('user_id', as_index=False)[['sad.depressed', 'open.stressed']].mean()

# Rename columns to match target schema
result.columns = ['user_id', 'sad', 'stressed']

# Save the result to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts_recovery_test_val.csv', index=False)