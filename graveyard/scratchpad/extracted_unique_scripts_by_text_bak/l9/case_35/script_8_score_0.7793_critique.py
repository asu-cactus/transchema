import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# UNION dimension tables (sources 0,1,8,9) - same schema
union_dim = pd.concat([source0, source1, source8, source9], ignore_index=True)

# Join union_dim with all aspect tables on ROW_WID
# Join with source2 (INBOUND_CALLS_NUM)
result_1 = pd.merge(union_dim, source2, on="ROW_WID", how="inner")

# Join with source3 (KEYWORDS_NUM)
result_2 = pd.merge(result_1, source3, on="ROW_WID", how="inner")

# Join with source4 (TECHSUPPORT_NUM)
result_3 = pd.merge(result_2, source4, on="ROW_WID", how="inner")

# Join with source5 (INTERACTIONS_NUM)
result_4 = pd.merge(result_3, source5, on="ROW_WID", how="inner")

# Join with source6 (COLLECTION_EVENTS_NUM)
result_5 = pd.merge(result_4, source6, on="ROW_WID", how="inner")

# Join with source7 (VISITS_NUM)
result_6 = pd.merge(result_5, source7, on="ROW_WID", how="inner")

# Project only TECHSUPPORT_NUM as target schema requires
final_output = result_6[["TECHSUPPORT_NUM"]]

# Write to target file
final_output.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)