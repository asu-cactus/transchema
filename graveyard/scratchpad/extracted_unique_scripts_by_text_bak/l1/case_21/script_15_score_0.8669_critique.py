import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_21/training_*.csv")

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df = pd.concat(df_list, ignore_index=True)

# Strip whitespace from Major_category
df["Major_category"] = df["Major_category"].str.strip()

# Group by Major_category and aggregate mean of Median
result = df.groupby("Major_category", as_index=False)["Median"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)