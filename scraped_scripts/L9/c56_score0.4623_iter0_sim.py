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

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('last_pymnt_d', as_index=False).size()
result = result.rename(columns={'size': 'last_pymnt_d'})
# The above line renames 'size' to 'last_pymnt_d' which is incorrect because size() returns counts.
# The target schema is ['last_pymnt_d': integer] and target examples show last_pymnt_d values as counts per last_pymnt_d.
# So the groupby count per last_pymnt_d is the count of rows per last_pymnt_d, but the target examples show last_pymnt_d as integer values (like 76, 11, 32).
# So the target column is the count of occurrences per last_pymnt_d value.

# So the correct output is a dataframe with columns: last_pymnt_d (the group key) and the count of occurrences (integer).
# But the target schema only has one column named last_pymnt_d, which is integer.
# The target examples show last_pymnt_d values like 76, 11, 32, which are counts.

# So the target table is a count of occurrences per last_pymnt_d value, but the column is named last_pymnt_d.

# So we should rename the count column to last_pymnt_d and the group key column to something else or drop it?

# But the target schema only has one column named last_pymnt_d.

# So the output should be a dataframe with one column last_pymnt_d, whose values are counts of occurrences per last_pymnt_d.

# So we can do:
counts = df_all['last_pymnt_d'].value_counts().sort_index()
result = counts.reset_index(drop=True)
result = pd.DataFrame({'last_pymnt_d': counts.values})

# Save result
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_56/target_multisource_mcts.csv", index=False)