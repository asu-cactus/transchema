import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# Union the dimension tables with the same schema
union_5_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

# Join all tables on ROW_WID
j1 = pd.merge(union_5_8, s0, on="ROW_WID", how="inner")
j2 = pd.merge(j1, s1, on="ROW_WID", how="inner")
j3 = pd.merge(j2, s2, on="ROW_WID", how="inner")
j4 = pd.merge(j3, s3, on="ROW_WID", how="inner")
j5 = pd.merge(j4, s4, on="ROW_WID", how="inner")
j6 = pd.merge(j5, s9, on="ROW_WID", how="inner")

# Group by ROW_WID and aggregate VISITS_NUM by mean to handle duplicates
agg = j6.groupby("ROW_WID", as_index=False).agg({"VISITS_NUM": "mean"})

# Convert VISITS_NUM to int (target schema is integer)
agg["VISITS_NUM"] = agg["VISITS_NUM"].astype(int)

# Output only VISITS_NUM column as per target schema
result = agg[["VISITS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)