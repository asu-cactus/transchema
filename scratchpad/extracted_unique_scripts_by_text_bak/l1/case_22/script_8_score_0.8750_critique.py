import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_22/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables
df_list = [pd.read_csv(f, index_col=0) for f in files]
df_union = pd.concat(df_list, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_union.groupby("condition", as_index=False)["click"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)