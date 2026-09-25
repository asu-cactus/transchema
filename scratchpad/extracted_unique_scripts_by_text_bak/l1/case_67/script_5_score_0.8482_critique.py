import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_67/training_*.csv")

# Read and concatenate all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)

# Group by user_id and aggregate mean on sad.depressed and open.stressed
result = df_all.groupby('user_id')[['sad.depressed', 'open.stressed']].mean().reset_index()

# Rename columns to match target schema
result = result.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)