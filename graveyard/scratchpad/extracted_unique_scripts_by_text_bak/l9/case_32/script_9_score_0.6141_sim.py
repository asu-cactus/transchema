import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

join_01 = pd.merge(s1, s0, on="ROW_WID", how="inner")
join_012 = pd.merge(join_01, s2, on="ROW_WID", how="inner")
join_0123 = pd.merge(join_012, s3, on="ROW_WID", how="inner")
join_01234 = pd.merge(join_0123, s4, on="ROW_WID", how="inner")

union_5678 = pd.concat([s5, s6, s7, s8], ignore_index=True)

join_all = pd.merge(join_01234, union_5678, on="ROW_WID", how="inner")
join_all = pd.merge(join_all, s9, on="ROW_WID", how="inner")

result = join_all.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "VISITS_NUM"})

# The target schema is ['VISITS_NUM': integer], but the groupby count is the count of rows per VISITS_NUM.
# The partial plan says GROUP_BY : [VISITS_NUM], which implies grouping by VISITS_NUM and counting rows.
# But the target examples show VISITS_NUM as the value, not a count.
# So the correct interpretation is to group by VISITS_NUM and count rows, but output VISITS_NUM and the count.
# The target schema only has VISITS_NUM column, so likely the count is the number of rows per VISITS_NUM.
# But the target examples show VISITS_NUM values, not counts.
# So we output VISITS_NUM as is, no aggregation needed.
# The partial plan is ambiguous, but since the target schema is only VISITS_NUM, we just output distinct VISITS_NUM values.

# So final output is distinct VISITS_NUM values from join_all.

final = join_all[["VISITS_NUM"]].drop_duplicates().reset_index(drop=True)
final["VISITS_NUM"] = final["VISITS_NUM"].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)