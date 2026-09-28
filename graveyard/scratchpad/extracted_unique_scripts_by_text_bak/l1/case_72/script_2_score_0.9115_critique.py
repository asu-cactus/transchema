import pandas as pd
import glob

# Read all source CSV files with the same schema
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_72/training_*.csv"
files = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and count rows per condition
result = df_all.groupby("condition", as_index=False).size()
result.columns = ["condition", "0"]

# Ensure correct types
result["condition"] = result["condition"].astype(int)
result["0"] = result["0"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)