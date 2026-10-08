import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_56/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_14.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables (concatenate)
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY last_pymnt_d and count occurrences
counts = df_all.groupby('last_pymnt_d', as_index=False).size()

# Rename count column to last_pymnt_d to match target schema
result = counts.rename(columns={'size': 'last_pymnt_d'})

# Save result
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_56/target_multisource_mcts.csv", index=False)