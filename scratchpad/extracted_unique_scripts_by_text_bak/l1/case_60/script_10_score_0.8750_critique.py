import pandas as pd

# Read all source tables (only one source table given here, but code is ready for multiple)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)

# If there were multiple source tables, we would read and union them here.
# Since only one source is given, union is just df0 itself.
df_all = df0

# Filter rows where type == "Urban"
df_filtered = df_all[df_all['type'] == "Urban"]

# Group by 'type' and sum 'driver_count'
result = df_filtered.groupby('type', as_index=False)['driver_count'].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)