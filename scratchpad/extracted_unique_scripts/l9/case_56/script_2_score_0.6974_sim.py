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

result = df_all.groupby('last_pymnt_d', as_index=False).size().rename(columns={'size':'last_pymnt_d'})

# The target schema expects 'last_pymnt_d' as integer counts per last_pymnt_d value
# The groupby count is the count of rows per last_pymnt_d, so rename accordingly:
result = result.rename(columns={'last_pymnt_d': 'last_pymnt_d', 'size': 'count'})
# But target schema only has one column 'last_pymnt_d' with integer values representing counts per last_pymnt_d
# So we must output a dataframe with columns: last_pymnt_d (the group key) and the count as integer values in that column
# The target examples show last_pymnt_d column with integer values like 28, 45, 30, which are counts per last_pymnt_d value

# So we should output a dataframe with columns: last_pymnt_d (the group key) and the count as integer values in that column
# But the target schema only has one column named last_pymnt_d, which holds the counts, so we must rename the count column to last_pymnt_d and drop the group key column

# Actually, the target schema is ['last_pymnt_d': integer], and the target examples show last_pymnt_d values like 28, 45, 30
# The partial plan says GROUP_BY : [last_pymnt_d], so the aggregation is count of rows per last_pymnt_d value
# So the output table has one column last_pymnt_d which is the count of rows per last_pymnt_d value

# So the final output is a dataframe with one column last_pymnt_d, which is the count of rows per last_pymnt_d value

# So rename the count column to last_pymnt_d and drop the original last_pymnt_d column (the group key)
result = df_all.groupby('last_pymnt_d').size().reset_index(name='count')
result = result.rename(columns={'count': 'last_pymnt_d'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_56/target_multisource_mcts.csv", index=False)