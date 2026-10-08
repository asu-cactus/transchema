import pandas as pd

# Read the single source table (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

# If there were multiple source tables, we would union them here, e.g.:
# df1 = pd.read_csv("path_to_source1.csv", index_col=0)
# df2 = pd.read_csv("path_to_source2.csv", index_col=0)
# df = pd.concat([df0, df1, df2], ignore_index=True)
# But since only one source is given, just use df0 as df

df = df0  # union of all source tables (only one here)

# Group by 'condition' and aggregate average of 'click'
grouped = df.groupby("condition", as_index=False).agg(click=("click", "mean"))

# Ensure correct types
grouped["condition"] = grouped["condition"].astype(int)
grouped["click"] = grouped["click"].astype(float)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)