import pandas as pd

# Read all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)  # ROW_WID, INBOUND_CALLS_NUM
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)  # ROW_WID, VISITS_NUM
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)  # ROW_WID, KEYWORDS_NUM
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)  # ROW_WID, INTERACTIONS_NUM
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)  # ROW_WID, COLLECTION_EVENTS_NUM
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)  # dimension table
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)  # dimension table
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)  # dimension table
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)  # dimension table
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)  # ROW_WID, TECHSUPPORT_NUM

# UNION dimension tables (src5, src6, src7, src8)
dim = pd.concat([src5, src6, src7, src8], ignore_index=True)

# Join dimension table with all aspect tables on ROW_WID
result = dim.merge(src0, on="ROW_WID", how="inner")
result = result.merge(src1, on="ROW_WID", how="inner")
result = result.merge(src2, on="ROW_WID", how="inner")
result = result.merge(src3, on="ROW_WID", how="inner")
result = result.merge(src4, on="ROW_WID", how="inner")
result = result.merge(src9, on="ROW_WID", how="inner")

# Project only VISITS_NUM as per target schema
result = result[["VISITS_NUM"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)