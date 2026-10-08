import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source tables)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_13/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read and concatenate all source tables
dfs = []
for f in files:
    df = pd.read_csv(f, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Select relevant columns and ensure correct types
df_all = df_all[['sex', 'smoker', 'tip_pct']].copy()
df_all['sex'] = df_all['sex'].astype(str)
df_all['smoker'] = df_all['smoker'].astype(str)
df_all['tip_pct'] = df_all['tip_pct'].astype(float)

# Group by sex and smoker, aggregate tip_pct by mean
result = df_all.groupby(['sex', 'smoker'], as_index=False).agg({'tip_pct': 'mean'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)