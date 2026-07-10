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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('last_credit_pull_d', as_index=False).size()
result.rename(columns={'size': 'last_credit_pull_d'}, inplace=True)
result = result.rename(columns={'last_credit_pull_d': 'count'})
result = result.rename(columns={'count': 'last_credit_pull_d'})

# The above renaming is incorrect logically, fix it:
# We want the groupby count per last_credit_pull_d, so the output should be:
# last_credit_pull_d (the group key) and count (the count)
# But target schema is ['last_credit_pull_d': integer] and target examples show counts as values.
# So the column name should be last_credit_pull_d and values are counts.

# So better to do:
result = df_all.groupby('last_credit_pull_d', as_index=False).size()
result.columns = ['last_credit_pull_d', 'count']
result = result.rename(columns={'count': 'last_credit_pull_d'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_57/target_multisource_mcts.csv", index=False)