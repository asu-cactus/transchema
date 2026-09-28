import pandas as pd
import glob

# Read all source files matching the pattern (assuming multiple source files exist)
# The problem states "all source tables must be used" and the source file path pattern is:
# autopipeline-benchmarks/github-pipelines/length1_54/training_*.csv
# So we read all files matching training_*.csv

file_pattern = "autopipeline-benchmarks/github-pipelines/length1_54/training_*.csv"
all_files = glob.glob(file_pattern)

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(f, index_col=0) for f in all_files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_all.groupby("condition", as_index=False)["click"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)