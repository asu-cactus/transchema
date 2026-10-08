import pandas as pd
import glob

# Read all source files matching the pattern (all source tables)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_22/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by 'condition' and sum 'click'
df_grouped = df_all.groupby("condition", as_index=False)["click"].sum()

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)