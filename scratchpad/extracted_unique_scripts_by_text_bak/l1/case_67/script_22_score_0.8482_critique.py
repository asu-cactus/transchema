import pandas as pd
import glob

# Read all source files matching the pattern (assuming multiple source files exist)
# Since only one source file is given, we read only that one.
# If multiple source files exist, adjust the path pattern accordingly.
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_67/training_*.csv")

# Read and concatenate all source tables (UNION)
df_list = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df = pd.concat(df_list, ignore_index=True)

# Group by user_id and aggregate mean on sad.depressed and open.stressed
result = df.groupby('user_id')[['sad.depressed', 'open.stressed']].mean().reset_index()

# Rename columns to match target schema
result = result.rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)