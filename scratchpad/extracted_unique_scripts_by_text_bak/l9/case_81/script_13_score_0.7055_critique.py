import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_81/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_9.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all source tables (UNION)
df = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes
df['admit'] = df['admit'].astype(int)
df['gre'] = df['gre'].astype(int)
df['gpa'] = df['gpa'].astype(float)
df['prestige'] = df['prestige'].astype(int)

# Group by admit, gre, prestige and aggregate gpa by mean
df_agg = df.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Write output with exact target schema column order
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length9_81/target_multisource_mcts.csv", index=False)