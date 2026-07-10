import pandas as pd

# Read the single source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

# Since only one source table is given, union is trivial (just df0)
# If there were multiple source tables, we would read and concat them here.

# Group by Gender and count occurrences
result = df0.groupby("Gender").size().reset_index(name='0')

# Ensure '0' column is integer type
result['0'] = result['0'].astype(int)

# Reorder columns to match target schema exactly
result = result[['Gender', '0']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)