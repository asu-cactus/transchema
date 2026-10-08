import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length4_85/training_9.csv",
]

# Read and union all source tables
dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    dfs.append(df[['crit_cn', 'critic']])

df_all = pd.concat(dfs, ignore_index=True)

# Drop rows with missing 'crit_cn' or 'critic'
df_all = df_all.dropna(subset=['crit_cn', 'critic'])

# Ensure 'critic' is numeric (for counting, values themselves don't matter)
df_all['critic'] = pd.to_numeric(df_all['critic'], errors='coerce')
df_all = df_all.dropna(subset=['critic'])

# Group by 'crit_cn' and count number of 'critic' entries per country
result = df_all.groupby('crit_cn', as_index=False).agg({'critic': 'count'})

# Rename columns to match target schema exactly
result.columns = ['crit_cn', 'critic']

# Convert 'critic' to int
result['critic'] = result['critic'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)