import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files exist)
# Since only one source file is given, this will read just that one.
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_60/training_*.csv")

# Read and union all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)

# Filter rows where type == 'Urban'
df_filtered = df_all[df_all['type'] == 'Urban']

# Group by 'type' and sum 'driver_count'
result = df_filtered.groupby('type', as_index=False)['driver_count'].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)