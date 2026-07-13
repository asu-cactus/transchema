import pandas as pd

# Load source data
df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_92/test_0.csv', index_col=0)

# Convert user_id to lowercase to match target format
df['user_id'] = df['user_id'].str.lower()

# GROUP BY user_id and take first occurrence (removes duplicates)
result = df.groupby('user_id', as_index=False).first()

# Save the result
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts_recovery_test_val.csv', index=False)