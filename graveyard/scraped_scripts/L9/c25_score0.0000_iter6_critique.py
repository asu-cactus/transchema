import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# Join the four tables with the same schema on ROW_WID using inner joins to avoid duplicates
df = s0.merge(s1, on="ROW_WID", how="inner", suffixes=('_s0', '_s1'))
df = df.merge(s4, on="ROW_WID", how="inner", suffixes=('', '_s4'))
df = df.merge(s5, on="ROW_WID", how="inner", suffixes=('', '_s5'))

# Join with the other six tables on ROW_WID using left joins to keep all rows from df
df = df.merge(s2, on="ROW_WID", how="left")
df = df.merge(s3, on="ROW_WID", how="left")
df = df.merge(s6, on="ROW_WID", how="left")
df = df.merge(s7, on="ROW_WID", how="left")
df = df.merge(s8, on="ROW_WID", how="left")
df = df.merge(s9, on="ROW_WID", how="left")

# Project CANCEL_DT column from the first table (s0) - after merges, CANCEL_DT is from s0 (no suffix)
result = df[["CANCEL_DT"]].copy()

# Keep CANCEL_DT as string type, preserving NaNs as 'nan' string is not desired, so keep original dtype
# But target examples show string with NaNs, so convert to string but keep NaNs as NaN
result["CANCEL_DT"] = result["CANCEL_DT"].astype("string")

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)