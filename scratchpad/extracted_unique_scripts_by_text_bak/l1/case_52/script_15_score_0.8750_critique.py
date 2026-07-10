import pandas as pd
import glob

# Read all source CSV files with the same schema
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_52/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables
df_list = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by 'condition' and sum 'click'
agg = df_all.groupby("condition", as_index=False)["click"].sum()

# Rename columns to match target schema
agg.columns = ["condition", "0"]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)