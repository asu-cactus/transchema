import pandas as pd
import glob

# Read all source CSV files matching the pattern (all source tables)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_29/training_*.csv"
files = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by Gender and count Purchase ID
result = df_all.groupby("Gender", as_index=False).agg({"Purchase ID": "count"}).rename(columns={"Purchase ID": "0"})

# Ensure '0' column is integer type
result["0"] = result["0"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)