import pandas as pd

# Read all source tables with index_col=0
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv", index_col=0)

# UNION the dimension tables with identical schema
dim_tables = [source2, source3, source6, source8]
unioned_dim = pd.concat(dim_tables, ignore_index=True)

# Join unioned_dim with source0 on ROW_WID
result_1 = pd.merge(unioned_dim, source0, on="ROW_WID", how="inner")

# Join with source1 on ROW_WID
result_2 = pd.merge(result_1, source1, on="ROW_WID", how="inner")

# Join with source4 on ROW_WID
result_3 = pd.merge(result_2, source4, on="ROW_WID", how="inner")

# Join with source5 on ROW_WID
result_4 = pd.merge(result_3, source5, on="ROW_WID", how="inner")

# Join with source7 on ROW_WID
result_5 = pd.merge(result_4, source7, on="ROW_WID", how="inner")

# Join with source9 on ROW_WID
final_result = pd.merge(result_5, source9, on="ROW_WID", how="inner")

# Select only the target column MONTHS_AGE
output = final_result[["MONTHS_AGE"]]

# Write to CSV without index as per usual convention
output.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)