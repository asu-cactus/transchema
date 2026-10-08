import pandas as pd

files = [
    "autopipeline-benchmarks/github-pipelines/length9_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_54/training_14.csv"
]

dfs = [pd.read_csv(f, index_col=0) for f in files]
union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby("earliest_cr_line", as_index=False).size()
result.rename(columns={"size": "earliest_cr_line"}, inplace=True)

# The target schema is ['earliest_cr_line': integer], but the target examples show earliest_cr_line as the grouping key, not the count.
# The partial plan says GROUP_BY : [earliest_cr_line], which implies grouping by earliest_cr_line.
# The target examples show earliest_cr_line values, not counts.
# So the final output should be the distinct earliest_cr_line values from all sources.
# Therefore, we just need to get unique earliest_cr_line values.

result = union_df[["earliest_cr_line"]].drop_duplicates().sort_values("earliest_cr_line").reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_54/target_multisource_mcts.csv", index=False)