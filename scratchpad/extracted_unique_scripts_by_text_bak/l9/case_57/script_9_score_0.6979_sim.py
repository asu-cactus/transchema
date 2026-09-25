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
result.columns = ['last_credit_pull_d', 'count']  # size() returns a Series, so convert to DataFrame with count column

# The target schema only has 'last_credit_pull_d' column, so we keep only that column.
# The target examples show only 'last_credit_pull_d' column, so we drop the count column.
result = result[['last_credit_pull_d']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_57/target_multisource_mcts.csv", index=False)