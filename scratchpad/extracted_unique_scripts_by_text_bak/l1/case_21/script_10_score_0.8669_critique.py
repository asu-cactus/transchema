import pandas as pd
import glob

# Read all source files matching the pattern (assuming all source files are in the same folder and named similarly)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_21/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read and concatenate all source tables
df_list = [pd.read_csv(f, index_col=0) for f in files]
df = pd.concat(df_list, ignore_index=True)

# Strip whitespace from "Major_category"
df["Major_category"] = df["Major_category"].str.strip()

# Group by "Major_category" and compute mean of "Median"
result = df.groupby("Major_category", as_index=False)["Median"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)