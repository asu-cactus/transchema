import pandas as pd

# Read all source tables (only one given here)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)

# Union all source tables (only one here)
df_all = pd.concat([df0], ignore_index=True)

# Filter rows where Major_category and Median are not null
df_filtered = df_all[df_all["Major_category"].notnull() & df_all["Median"].notnull()]

# Group by Major_category and compute mean of Median
result = df_filtered.groupby("Major_category", as_index=False)["Median"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)