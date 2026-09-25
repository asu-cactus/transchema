import pandas as pd

# Read dimension tables (all have same schema)
dim0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
dim1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
dim3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
dim5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

# Union dimension tables
dim_union = pd.concat([dim0, dim1, dim3, dim5], ignore_index=True)

# Read aspect tables
aspect2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
aspect4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
aspect6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
aspect7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
aspect8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
aspect9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# Join dimension union with each aspect table on ROW_WID
df = dim_union.merge(aspect2, on="ROW_WID", how="inner")
df = df.merge(aspect4, on="ROW_WID", how="inner")
df = df.merge(aspect6, on="ROW_WID", how="inner")
df = df.merge(aspect7, on="ROW_WID", how="inner")
df = df.merge(aspect8, on="ROW_WID", how="inner")
df = df.merge(aspect9, on="ROW_WID", how="inner")

# Project only HOME_PASSED column as per target schema
result = df[["HOME_PASSED"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)