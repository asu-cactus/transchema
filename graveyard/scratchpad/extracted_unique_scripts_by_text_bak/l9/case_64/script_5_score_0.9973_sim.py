import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_64/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# The partial plan suggests a JOIN between Source9_64_0 and Source9_64_9 on all columns.
# But since all sources have the same schema and the target schema matches,
# and the target examples count is 579 (sum of all rows),
# the best approach is to UNION all sources directly.

# Concatenate all dataframes (union)
result = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes as per target schema
result = result.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_64/target_multisource_mcts.csv", index=False)