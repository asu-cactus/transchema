import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

union_df = pd.concat([s0, s1, s3, s5], ignore_index=True)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

join_1 = pd.merge(union_df, s2, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s4, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s6, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s7, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="inner")

result = join_6.groupby("HOME_PASSED", as_index=False).size()
result = result.rename(columns={"size": "HOME_PASSED"})
# The above line is incorrect because groupby.size() returns a Series with counts, not the grouped column.
# We want to group by HOME_PASSED and produce a table with HOME_PASSED as integer column.
# The target schema is ['HOME_PASSED': integer], and target examples show values of HOME_PASSED.
# The partial plan says PIVOT and GROUP_BY on HOME_PASSED.
# The best interpretation is to group by HOME_PASSED and count rows per HOME_PASSED, but target examples show only HOME_PASSED column with values, no counts.
# So likely the target is just the distinct HOME_PASSED values from the joined data.
# So we just need unique HOME_PASSED values as integers.

result = join_6[["HOME_PASSED"]].drop_duplicates().reset_index(drop=True)
result["HOME_PASSED"] = result["HOME_PASSED"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)