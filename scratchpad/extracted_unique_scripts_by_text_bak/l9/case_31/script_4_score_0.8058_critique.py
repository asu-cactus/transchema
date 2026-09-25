import pandas as pd

# Read all source tables with index_col=0 as per Hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# UNION dimension tables (same schema)
dim_union = pd.concat([source0, source1, source3, source5], ignore_index=True)

# Join with aspect tables on ROW_WID
# Join with source2
df = dim_union.merge(source2, on="ROW_WID", how="inner")

# Join with source4
df = df.merge(source4, on="ROW_WID", how="inner")

# Join with source6
df = df.merge(source6, on="ROW_WID", how="inner")

# Join with source7
df = df.merge(source7, on="ROW_WID", how="inner")

# Join with source8
df = df.merge(source8, on="ROW_WID", how="inner")

# Join with source9
df = df.merge(source9, on="ROW_WID", how="inner")

# Project only HOME_PASSED as per target schema
result = df[["HOME_PASSED"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)