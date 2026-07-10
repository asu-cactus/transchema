import pandas as pd

# Read the source CSV with index_col=0 as instructed
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

# Filter rows where AGI_STUB == 21
df_filtered = df[df['AGI_STUB'] == 21]

# Select only the target columns
df_target = df_filtered[['zipcode', 'AGI_STUB', 'N1', 'A00100']]

# Write the output CSV with the exact target schema and column names
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)