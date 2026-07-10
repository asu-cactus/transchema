import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# UNION the 4 big tables with same schema
union_0_1_8_9 = pd.concat([s0, s1, s8, s9], ignore_index=True)

# JOIN union with s4 (which has TECHSUPPORT_NUM)
join_0_1_8_9_4 = pd.merge(union_0_1_8_9, s4, on="ROW_WID", how="inner")

# JOIN with other aspect tables on ROW_WID
join_0_1_8_9_4_2 = pd.merge(join_0_1_8_9_4, s2, on="ROW_WID", how="inner")
join_0_1_8_9_4_2_3 = pd.merge(join_0_1_8_9_4_2, s3, on="ROW_WID", how="inner")
join_0_1_8_9_4_2_3_5 = pd.merge(join_0_1_8_9_4_2_3, s5, on="ROW_WID", how="inner")
join_0_1_8_9_4_2_3_5_6 = pd.merge(join_0_1_8_9_4_2_3_5, s6, on="ROW_WID", how="inner")
join_0_1_8_9_4_2_3_5_6_7 = pd.merge(join_0_1_8_9_4_2_3_5_6, s7, on="ROW_WID", how="inner")

# Select distinct TECHSUPPORT_NUM values
result = join_0_1_8_9_4_2_3_5_6_7[["TECHSUPPORT_NUM"]].drop_duplicates().copy()

# Ensure TECHSUPPORT_NUM is integer type
result["TECHSUPPORT_NUM"] = result["TECHSUPPORT_NUM"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)