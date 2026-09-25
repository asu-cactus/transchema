import pandas as pd

# Read all source tables
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

# Union the dimension tables with same schema
union_dim = pd.concat([s2, s5, s6, s8], ignore_index=True)

# Join unioned dimension table with all other aspect tables on ROW_WID
df = union_dim.merge(s0, on="ROW_WID", how="inner")
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s3, on="ROW_WID", how="inner")
df = df.merge(s4, on="ROW_WID", how="inner")
df = df.merge(s7, on="ROW_WID", how="inner")
df = df.merge(s9, on="ROW_WID", how="inner")

# Select only the target column
result = df[["KEYWORDS_NUM"]].copy()
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)