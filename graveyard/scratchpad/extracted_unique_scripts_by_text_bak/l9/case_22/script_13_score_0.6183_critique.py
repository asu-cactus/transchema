import pandas as pd

# Read all sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# Union dimension tables (same schema)
dim_union = pd.concat([source3, source4, source7, source8], ignore_index=True)

# Join dimension union with aspect tables on ROW_WID
merged = dim_union.merge(source0, on="ROW_WID", how="inner")
merged = merged.merge(source1, on="ROW_WID", how="inner")
merged = merged.merge(source2, on="ROW_WID", how="inner")
merged = merged.merge(source5, on="ROW_WID", how="inner")
merged = merged.merge(source6, on="ROW_WID", how="inner")
merged = merged.merge(source9, on="ROW_WID", how="inner")

# Project only INBOUND_CALLS_NUM as per target schema
final = merged[["INBOUND_CALLS_NUM"]]

# Remove duplicates if any (target examples suggest unique rows)
final = final.drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)