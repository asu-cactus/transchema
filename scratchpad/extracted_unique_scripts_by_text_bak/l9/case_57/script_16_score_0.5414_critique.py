import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_14.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY last_credit_pull_d and count occurrences
result = df_all.groupby('last_credit_pull_d', as_index=False).size()

# Rename columns: 'last_credit_pull_d' is the group key, 'size' is the count
result.columns = ['last_credit_pull_d', 'count']

# The target schema expects a single column named 'last_credit_pull_d' with counts as values
# So output only the counts as a single column named 'last_credit_pull_d'
result = result[['count']].rename(columns={'count': 'last_credit_pull_d'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_57/target_multisource_mcts.csv", index=False)