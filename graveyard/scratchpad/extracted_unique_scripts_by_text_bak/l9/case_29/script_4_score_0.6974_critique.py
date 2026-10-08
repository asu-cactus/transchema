import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

# UNION the four dimension tables with the same schema
union_2_5_6_9 = pd.concat([s2, s5, s6, s9], ignore_index=True)

# JOIN unioned dimension table with s0 on ROW_WID
result = pd.merge(union_2_5_6_9, s0, on="ROW_WID", how="inner")

# JOIN with s1
result = pd.merge(result, s1, on="ROW_WID", how="inner")

# JOIN with s3
result = pd.merge(result, s3, on="ROW_WID", how="inner")

# JOIN with s4
result = pd.merge(result, s4, on="ROW_WID", how="inner")

# JOIN with s7
result = pd.merge(result, s7, on="ROW_WID", how="inner")

# JOIN with s8
result = pd.merge(result, s8, on="ROW_WID", how="inner")

# Project only COLLECTION_EVENTS_NUM column as per target schema
result = result[["COLLECTION_EVENTS_NUM"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)