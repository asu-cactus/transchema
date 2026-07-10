import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_97/training_*.csv"
all_files = glob.glob(file_pattern)

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(f, index_col=0) for f in all_files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by 'crit_cn' and count 'critic'
result = df_all.groupby("crit_cn", as_index=False).agg(critic=("critic", "count"))

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)