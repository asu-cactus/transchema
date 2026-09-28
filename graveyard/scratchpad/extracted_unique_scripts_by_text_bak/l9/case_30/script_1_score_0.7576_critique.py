import pandas as pd

# Read and union the dimension tables with the same schema
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

union_dim = pd.concat([s3, s4, s5, s7], ignore_index=True)

# Read the other source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

# Join all tables on ROW_WID
df = union_dim.merge(s0, on="ROW_WID", how="inner")
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s2, on="ROW_WID", how="inner")
df = df.merge(s6, on="ROW_WID", how="inner")
df = df.merge(s8, on="ROW_WID", how="inner")
df = df.merge(s9, on="ROW_WID", how="inner")

# Select only the ARPU column as per target schema
result = df[["ARPU"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)