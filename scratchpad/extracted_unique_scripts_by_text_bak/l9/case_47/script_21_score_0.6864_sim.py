import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)
grouped = union_df.groupby('int_rate', as_index=False).size()
grouped.rename(columns={'size': 'int_rate'}, inplace=True)
# The target schema is ['int_rate': integer], but the target examples show int_rate as the grouped key,
# so we keep the int_rate column as integer and the count as the value.
# The target examples show only one column named int_rate, which is the grouped key.
# So we output the grouped keys only (the unique int_rate values).
# But the partial plan says to count occurrences, so the count is the aggregation.
# The target examples show int_rate values only, so we output the grouped keys only.
# To match the target schema exactly, output the grouped keys only (drop counts).
# But the partial plan implies counting occurrences, so we keep counts as int_rate column.
# To resolve this, rename the count column to int_rate and output that.
# This matches the example target examples where int_rate column contains counts.
# So the final output is the count of each int_rate value, with int_rate as the count column.

# The above reasoning is contradictory, but the partial plan and examples imply the target table has int_rate as the count of occurrences per int_rate value.
# So we keep the count as int_rate column.

grouped = union_df.groupby('int_rate', as_index=False).size()
grouped.rename(columns={'size': 'int_rate'}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)