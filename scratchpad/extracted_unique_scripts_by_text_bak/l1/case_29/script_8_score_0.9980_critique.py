import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_29/training_*.csv"
file_list = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in file_list]
df_all = pd.concat(dfs, ignore_index=True)

# Group by Gender and count Purchase ID
result = df_all.groupby("Gender", dropna=False).agg({"Purchase ID": "count"}).reset_index()

# Rename columns to match target schema
result.columns = ["Gender", "0"]

# Ensure correct types
result["Gender"] = result["Gender"].astype(str)
result["0"] = result["0"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)