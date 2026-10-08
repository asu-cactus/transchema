import pandas as pd

# Read the source table(s)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

# If there were multiple source tables, we would read and union them here.
# Since only one source table is given, we proceed with it.

# Select relevant columns
df = df0[['zipcode', 'AGI_STUB', 'N1', 'A00100']].copy()

# Convert to integer types as per target schema
df = df.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

# Group by the leftmost key columns and aggregate sums of value columns
df_result = df.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1': 'sum', 'A00100': 'sum'})

# Write the result to the target file
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)