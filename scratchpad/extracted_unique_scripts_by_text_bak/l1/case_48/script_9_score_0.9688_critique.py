import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_48/training_*.csv"
files = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by "Text Date" and sum "Water Use" and "Power Use"
agg_df = df_all.groupby("Text Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

# Rename "Text Date" to "Date"
agg_df = agg_df.rename(columns={"Text Date": "Date"})

# Cast columns to correct types
agg_df["Water Use"] = agg_df["Water Use"].astype(float)
agg_df["Power Use"] = agg_df["Power Use"].astype(int)

# Reorder columns to match target schema
agg_df = agg_df[["Date", "Water Use", "Power Use"]]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)