import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_34/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read all source tables into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in files]

# Union all source tables (concatenate)
df_union = pd.concat(dfs, ignore_index=True)

# Rename column J_CALL to V_GENE
df_union = df_union.rename(columns={"J_CALL": "V_GENE"})

# Write the final output
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)