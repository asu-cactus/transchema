import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

# UNION dimension tables (sources 2,5,6,9)
union_dim = pd.concat([df2, df5, df6, df9], ignore_index=True)

# Join unioned dimension table with Source0 on ROW_WID
result = pd.merge(union_dim, df0, on="ROW_WID", how="inner")

# Join with other aspect tables on ROW_WID
result = pd.merge(result, df1, on="ROW_WID", how="inner")
result = pd.merge(result, df3, on="ROW_WID", how="inner")
result = pd.merge(result, df4, on="ROW_WID", how="inner")
result = pd.merge(result, df7, on="ROW_WID", how="inner")
result = pd.merge(result, df8, on="ROW_WID", how="inner")

# Select distinct COLLECTION_EVENTS_NUM values
result = result[["COLLECTION_EVENTS_NUM"]].drop_duplicates().reset_index(drop=True)

# Ensure integer type as in target schema
result["COLLECTION_EVENTS_NUM"] = result["COLLECTION_EVENTS_NUM"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)