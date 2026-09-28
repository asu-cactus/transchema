import pandas as pd

# Read all source tables with index_col=0 to ignore numerical index column
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

# UNION dimension tables (all have same schema)
dim_union = pd.concat([source3, source4, source5, source7], ignore_index=True)

# Join dimension union with each aspect table on ROW_WID using inner join
df = dim_union.merge(source0, on="ROW_WID", how="inner")
df = df.merge(source1, on="ROW_WID", how="inner")
df = df.merge(source2, on="ROW_WID", how="inner")
df = df.merge(source6, on="ROW_WID", how="inner")
df = df.merge(source8, on="ROW_WID", how="inner")
df = df.merge(source9, on="ROW_WID", how="inner")

# Project only ARPU column as per target schema
result = df[["ARPU"]]

# Write output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)