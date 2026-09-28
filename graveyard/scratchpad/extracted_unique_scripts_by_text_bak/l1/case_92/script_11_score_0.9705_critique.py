import pandas as pd

# Read the single source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

# Lowercase user_id column
df0['user_id'] = df0['user_id'].str.lower()

# Since only one source table is given, union is trivial (just df0)
result = pd.concat([df0], ignore_index=True)

# Project columns in target schema order
result = result[['user_id', 'email', 'geo']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)