import pandas as pd

# Read all source tables
s9_34_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s9_34_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s9_34_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s9_34_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s9_34_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s9_34_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s9_34_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s9_34_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s9_34_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
s9_34_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# UNION the dimension tables with identical schema
dim_union = pd.concat([s9_34_2, s9_34_5, s9_34_6, s9_34_8], ignore_index=True)

# Join dimension union with all aspect tables on ROW_WID
result = dim_union.merge(s9_34_0, on="ROW_WID", how="inner")
result = result.merge(s9_34_1, on="ROW_WID", how="inner")
result = result.merge(s9_34_3, on="ROW_WID", how="inner")
result = result.merge(s9_34_4, on="ROW_WID", how="inner")
result = result.merge(s9_34_7, on="ROW_WID", how="inner")
result = result.merge(s9_34_9, on="ROW_WID", how="inner")

# Select distinct KEYWORDS_NUM values as target schema only has this column
result = result[["KEYWORDS_NUM"]].drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)