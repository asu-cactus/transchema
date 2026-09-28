import pandas as pd

# Read dimension tables with same schema
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# Union dimension tables
unioned_dim = pd.concat([s0, s1, s8, s9], ignore_index=True)

# Read aspect tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

# Join all aspect tables to the unioned dimension table on ROW_WID using left joins to keep all dimension rows
join_1 = pd.merge(unioned_dim, s2, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s5, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s6, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, s7, on="ROW_WID", how="left")

# Select only the target column TECHSUPPORT_NUM
result = join_6[["TECHSUPPORT_NUM"]].copy()

# Ensure correct integer type with nullable Int64 dtype
result["TECHSUPPORT_NUM"] = result["TECHSUPPORT_NUM"].astype("Int64")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)