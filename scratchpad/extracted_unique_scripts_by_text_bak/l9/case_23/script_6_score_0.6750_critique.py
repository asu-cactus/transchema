import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv", index_col=0)

# Join all tables step by step on ROW_WID using inner joins
result = pd.merge(s2, s0, on="ROW_WID", how="inner")
result = pd.merge(result, s1, on="ROW_WID", how="inner")
result = pd.merge(result, s3, on="ROW_WID", how="inner")
result = pd.merge(result, s4, on="ROW_WID", how="inner")
result = pd.merge(result, s5, on="ROW_WID", how="inner")
result = pd.merge(result, s6, on="ROW_WID", how="inner")
result = pd.merge(result, s7, on="ROW_WID", how="inner")
result = pd.merge(result, s8, on="ROW_WID", how="inner")
result = pd.merge(result, s9, on="ROW_WID", how="inner")

# Project only the target column MONTHS_AGE
target = result[["MONTHS_AGE"]].copy()

# Write output
target.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)