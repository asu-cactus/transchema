import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# Union the canceled-related sources (s2, s5, s6, s8) which share the same schema
canceled_union = pd.concat([s2, s5, s6, s8], ignore_index=True)

# Join canceled_union with s0 on ROW_WID
join_0 = pd.merge(canceled_union, s0, on="ROW_WID", how="inner")

# Join with s1
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")

# Join with s3
join_3 = pd.merge(join_1, s3, on="ROW_WID", how="inner")

# Join with s4
join_4 = pd.merge(join_3, s4, on="ROW_WID", how="inner")

# Join with s7
join_7 = pd.merge(join_4, s7, on="ROW_WID", how="inner")

# Join with s9 (which has KEYWORDS_NUM)
final_join = pd.merge(join_7, s9, on="ROW_WID", how="inner")

# Project only KEYWORDS_NUM column as target schema requires only that column
result = final_join[["KEYWORDS_NUM"]].copy()

# Ensure KEYWORDS_NUM is integer type as per target schema
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype("Int64")

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)