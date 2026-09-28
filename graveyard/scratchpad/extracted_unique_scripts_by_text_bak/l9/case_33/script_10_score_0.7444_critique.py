import pandas as pd

# Read all source tables with index_col=0 as per Hint 22
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)

# UNION the dimension tables (all have same schema)
unioned_dim = pd.concat([source4, source5, source7, source9], ignore_index=True)

# Join unioned_dim with each aspect table on ROW_WID
# Use inner joins to keep only matching ROW_WIDs (Hint 17)
result = unioned_dim.merge(source0, on="ROW_WID", how="inner")
result = result.merge(source1, on="ROW_WID", how="inner")
result = result.merge(source2, on="ROW_WID", how="inner")
result = result.merge(source3, on="ROW_WID", how="inner")
result = result.merge(source6, on="ROW_WID", how="inner")
result = result.merge(source8, on="ROW_WID", how="inner")

# Project only INTERACTIONS_NUM as per target schema
final_result = result[["INTERACTIONS_NUM"]]

# Write output CSV without index as per usual convention
final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)