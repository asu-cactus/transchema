import pandas as pd
import glob

# Read all source CSV files matching the pattern (all source tables)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_87/training_*.csv"
file_list = sorted(glob.glob(file_pattern))

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in file_list]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and aggregate mean on 'click'
result = df_all.groupby("condition", as_index=False)["click"].mean()

# Cast types to match target schema
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)