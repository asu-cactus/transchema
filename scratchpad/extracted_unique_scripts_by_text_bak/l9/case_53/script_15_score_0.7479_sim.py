import pandas as pd

files = [
    "autopipeline-benchmarks/github-pipelines/length9_53/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_14.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in files]

union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby("addr_state", as_index=False).size().rename(columns={"size": "count"})

# The target schema only has 'addr_state' column, so we keep only that column.
# The target examples show only addr_state column, so we drop the count column.
# The GROUP_BY operation implies grouping by addr_state, but target schema has only addr_state column.
# So the final output is the distinct addr_state values (unique addr_state values).

result = result[["addr_state"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_53/target_multisource_mcts.csv", index=False)