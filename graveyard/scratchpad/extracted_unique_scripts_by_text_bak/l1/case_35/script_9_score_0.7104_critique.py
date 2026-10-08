import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_35/training_*.csv"
all_files = glob.glob(file_pattern)

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in all_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'Source Zipcode' and sum 'Counts'
result = df_all.groupby("Source Zipcode", as_index=False)["Counts"].sum()

# Ensure correct types
result["Source Zipcode"] = result["Source Zipcode"].astype(int)
result["Counts"] = result["Counts"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)