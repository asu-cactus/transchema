import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_0/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_0/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)
result = union_df.groupby('0', as_index=False).size().rename(columns={'size': 'count'})

# The target schema is ['0'] only, so we keep only the grouped key column '0'
# The partial plan says GROUP_BY : [0], but target schema is just ['0'] integer column.
# The target examples show values in '0' column, so the aggregation is likely sum of counts per '0' value.
# But since the target schema is only ['0'], and the examples show values like 368, 0, etc., it means the aggregation is sum of the values in '0' column grouped by '0' itself.
# This is a bit ambiguous because grouping by '0' and summing '0' is trivial (each group is a single value).
# Instead, we interpret the operation as summing all values in '0' column (since the target examples show large numbers).
# So we do groupby on the index (which is ignored), or just sum all values.

# Actually, since the source tables have only one column '0' with integer values, and the target schema is ['0'] integer,
# and the partial plan says GROUP_BY : [0], it means group by the values in '0' and count how many times each value appears.
# But the target examples show values like 368, 0, etc. which are not counts of distinct values but sums of values.

# Reconsider: The partial plan is GROUP_BY : [0], so group by the column '0' and aggregate something.
# The target schema is ['0'] integer, so the output is a single column '0' with integer values.
# The source tables have only one column '0' with integer values.
# The only meaningful aggregation is sum of '0' grouped by some key.
# But the only column is '0', so grouping by '0' itself means grouping by the values in '0' and counting or summing.
# This would produce a frequency table of values in '0', which does not match the target examples.

# Alternatively, the partial plan is a hint, but the actual operation is to sum all values from all source tables into a single integer column '0'.
# The target examples show a single column with values like 368, 0, etc., and 210 rows total.
# So the target table has 210 rows, each with a single integer value.

# Since the source tables have 20 or 10 rows each, total rows are 210 (20*10 + 10), matching target rows.
# So the operation is just concatenation of all source tables (union), no aggregation.

# Therefore, the partial plan GROUP_BY : [0] is likely a hint to group by the index (which is ignored), or a misinterpretation.

# Final decision: concatenate all source tables vertically, ignoring index, to get 210 rows with column '0'.

final_df = pd.concat(dfs, ignore_index=True)
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_0/target_multisource_mcts.csv", index=False)