import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files exist)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_72/training_*.csv"
all_files = glob.glob(file_pattern)

# Read and concatenate all source tables (UNION)
df_list = [pd.read_csv(f, index_col=0) for f in all_files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_all.groupby("condition", as_index=False)["click"].sum()

# Rename columns to match target schema
result.columns = ["condition", "0"]

# Ensure correct types
result["condition"] = result["condition"].astype(int)
result["0"] = result["0"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)