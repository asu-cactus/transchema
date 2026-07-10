import pandas as pd

# Read all sources
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

# Union the four large tables with same schema
union_5_6_7_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

# Start from s1 (has VISITS_NUM), left join union_5_6_7_8 on ROW_WID
join_1 = pd.merge(s1, union_5_6_7_8, on="ROW_WID", how="left")

# Left join other sources on ROW_WID
join_2 = pd.merge(join_1, s0, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s2, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s3, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s4, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="left")

# Project VISITS_NUM and cast to integer type
result = join_6[["VISITS_NUM"]].copy()
result["VISITS_NUM"] = result["VISITS_NUM"].astype("Int64")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)