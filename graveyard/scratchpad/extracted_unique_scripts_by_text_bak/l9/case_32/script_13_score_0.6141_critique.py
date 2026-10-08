import pandas as pd

# Read all source tables
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

# UNION the dimension tables s5, s6, s7, s8
union_5_6_7_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

# Join unioned dimension table with all aspect tables on ROW_WID
join_0 = pd.merge(union_5_6_7_8, s0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s3, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s4, on="ROW_WID", how="inner")
final_join = pd.merge(join_4, s9, on="ROW_WID", how="inner")

# Group by VISITS_NUM and count rows (ROW_WID) per VISITS_NUM
result = final_join.groupby("VISITS_NUM", as_index=False).agg({"ROW_WID": "count"})

# Rename count column to VISITS_NUM as per target schema
result = result.rename(columns={"ROW_WID": "VISITS_NUM"})

# Ensure VISITS_NUM is integer type
result["VISITS_NUM"] = result["VISITS_NUM"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)