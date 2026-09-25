import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_39/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_39/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby('0', as_index=False).size().rename(columns={'size': '0'})

# The groupby key is '0', but the target schema expects column '0' as integer values.
# The groupby size counts occurrences, but target examples show values that are sums of source '0' values.
# So instead of counting rows, we should sum the values grouped by '0'.

# Correcting aggregation to sum:
result = union_df.groupby('0', as_index=False)['0'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_39/target_multisource_mcts.csv", index=False)