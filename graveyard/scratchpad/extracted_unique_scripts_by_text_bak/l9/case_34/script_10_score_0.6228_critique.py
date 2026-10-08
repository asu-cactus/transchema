import pandas as pd

# Read all sources
source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# UNION dimension tables (sources 2,5,6,8)
dim_union = pd.concat([source_2, source_5, source_6, source_8], ignore_index=True)

# Join dimension union with source_0 on ROW_WID
joined_0 = pd.merge(dim_union, source_0, on="ROW_WID", how="inner")

# Join with source_1
joined_1 = pd.merge(joined_0, source_1, on="ROW_WID", how="inner")

# Join with source_3
joined_2 = pd.merge(joined_1, source_3, on="ROW_WID", how="inner")

# Join with source_4
joined_3 = pd.merge(joined_2, source_4, on="ROW_WID", how="inner")

# Join with source_7
joined_4 = pd.merge(joined_3, source_7, on="ROW_WID", how="inner")

# Join with source_9
joined_5 = pd.merge(joined_4, source_9, on="ROW_WID", how="inner")

# Project KEYWORDS_NUM and drop duplicates, sort for consistent output
result = joined_5[["KEYWORDS_NUM"]].drop_duplicates().sort_values("KEYWORDS_NUM").reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)