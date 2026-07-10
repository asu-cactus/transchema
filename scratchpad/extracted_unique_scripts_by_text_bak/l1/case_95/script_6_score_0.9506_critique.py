import pandas as pd
import glob

# Read all source CSV files matching the pattern (all source tables)
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_95/training_*.csv")

# Read and concatenate all source tables (UNION)
df_list = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(df_list, ignore_index=True)

# Group by customer_id and aggregate date by min
df_grouped = df_all.groupby("customer_id", as_index=False).agg({"date": "min"})

# Ensure correct types
df_grouped["customer_id"] = df_grouped["customer_id"].astype(int)
df_grouped["date"] = df_grouped["date"].astype(str)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)