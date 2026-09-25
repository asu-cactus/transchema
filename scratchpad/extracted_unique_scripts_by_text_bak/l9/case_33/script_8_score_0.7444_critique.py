import pandas as pd

# Read all source tables with index_col=0
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)

# UNION the dimension tables (all have same schema)
dim_union = pd.concat([source_4, source_5, source_7, source_9], ignore_index=True)

# Join dimension union with each aspect table on ROW_WID using inner join
result = dim_union.merge(source_0, on="ROW_WID", how="inner")
result = result.merge(source_1, on="ROW_WID", how="inner")
result = result.merge(source_2, on="ROW_WID", how="inner")
result = result.merge(source_3, on="ROW_WID", how="inner")
result = result.merge(source_6, on="ROW_WID", how="inner")
result = result.merge(source_8, on="ROW_WID", how="inner")

# Project only INTERACTIONS_NUM as per target schema
final_result = result[["INTERACTIONS_NUM"]]

# Write output CSV without index
final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)