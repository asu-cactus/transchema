import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

union_4_5_7_9 = pd.concat([s4, s5, s7, s9], ignore_index=True)

join_0 = pd.merge(union_4_5_7_9, s0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s3, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s6, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="inner")

result = join_5.groupby("INTERACTIONS_NUM", as_index=False).size().rename(columns={"size": "INTERACTIONS_NUM"})

# The target schema is ['INTERACTIONS_NUM': integer], but the target examples show INTERACTIONS_NUM as values, not counts.
# The partial plan suggests GROUP_BY on INTERACTIONS_NUM, but the target examples show INTERACTIONS_NUM as a column of values, not counts.
# So the group_by is likely to count occurrences of INTERACTIONS_NUM values.
# But the target examples show INTERACTIONS_NUM values, not counts.
# So we should output the distinct INTERACTIONS_NUM values with their counts.

# The groupby size() returns counts per INTERACTIONS_NUM value, but the target examples show INTERACTIONS_NUM as the value itself.
# So the target table is just the distinct INTERACTIONS_NUM values, not counts.

# Therefore, output distinct INTERACTIONS_NUM values from join_5.

final = join_5[["INTERACTIONS_NUM"]].drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)