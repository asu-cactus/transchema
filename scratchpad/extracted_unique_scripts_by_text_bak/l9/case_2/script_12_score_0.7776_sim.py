import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_2/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby('0', as_index=False).size().rename(columns={'size': 'count'})

# The target schema is ['0'] with integer values, and target examples show counts of occurrences of '0' values.
# So the final output is the grouped '0' values with their counts as the frequency of each unique '0' value.

# But the target schema only has one column '0' (integer). The examples show values like 0, 25, 203, 148, etc.
# The partial plan says PIVOT and GROUP_BY [0], which implies counting occurrences of each unique '0' value.

# Since the target schema has only one column '0', and the examples show counts, it means the output is the counts of each unique '0' value.
# So we need to output the counts as the '0' column.

# So rename the count column to '0' and convert to int
result = result.rename(columns={'count': '0'})
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_2/target_multisource_mcts.csv", index=False)