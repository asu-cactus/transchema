import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_48/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)
grouped = union_result.groupby('sub_grade', as_index=False).size()
grouped.rename(columns={'size': 'sub_grade'}, inplace=True)
# The target schema is ['sub_grade': integer], but the target examples show sub_grade as counts.
# The partial plan suggests grouping by sub_grade and counting occurrences.
# So the output column should be named 'sub_grade' and contain the counts.

# The groupby.size() returns a Series with name 'size', so we rename it to 'sub_grade' to match target schema.
# The dtype is integer by default.

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_48/target_multisource_mcts.csv", index=False)