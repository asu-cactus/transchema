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

join_1_9 = pd.merge(s1, s9, on="ROW_WID", how="inner")
join_0 = pd.merge(join_1_9, s0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_0, s2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s3, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s4, on="ROW_WID", how="inner")

union_5_6_7_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

final_join = pd.merge(join_4, union_5_6_7_8, on="ROW_WID", how="inner")

result = final_join.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "VISITS_NUM"})

# The target schema is ['VISITS_NUM': integer], and the target examples show VISITS_NUM as the count of visits.
# The groupby count above counts rows per VISITS_NUM value, but the target examples show VISITS_NUM as the grouping key.
# So the correct output is just the distinct VISITS_NUM values from s1 (or from the join), no aggregation count needed.
# The partial plan says GROUP_BY : [VISITS_NUM], but no aggregation specified.
# Since target examples show VISITS_NUM as integer values, and 4161 rows, likely the target is distinct VISITS_NUM values.
# So we output distinct VISITS_NUM values.

result = final_join[["VISITS_NUM"]].drop_duplicates().reset_index(drop=True)
result["VISITS_NUM"] = result["VISITS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)