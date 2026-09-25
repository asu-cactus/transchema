import pandas as pd

# Read all sources with index_col=0 to ignore the first numerical index column
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

# UNION the dimension tables (all have the same schema)
dim_union = pd.concat([s2, s5, s6, s8], ignore_index=True)

# Join dimension union with all aspect tables on ROW_WID
j0 = pd.merge(dim_union, s0, on="ROW_WID", how="inner")
j1 = pd.merge(j0, s1, on="ROW_WID", how="inner")
j2 = pd.merge(j1, s3, on="ROW_WID", how="inner")
j3 = pd.merge(j2, s4, on="ROW_WID", how="inner")
j4 = pd.merge(j3, s7, on="ROW_WID", how="inner")
j5 = pd.merge(j4, s9, on="ROW_WID", how="inner")

# The target schema is only KEYWORDS_NUM, so select distinct KEYWORDS_NUM
result = j5[["KEYWORDS_NUM"]].drop_duplicates().reset_index(drop=True)

# Ensure KEYWORDS_NUM is integer type as in target schema
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)