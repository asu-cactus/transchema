import pandas as pd

# Read all source tables with index_col=0 as per hint 22
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# UNION all dimension tables with same schema
dim_tables = [source0, source1, source4, source5]
unioned_dim = pd.concat(dim_tables, ignore_index=True)

# Join unioned_dim with all aspect tables on ROW_WID
result = unioned_dim.merge(source2, on="ROW_WID", how="inner")
result = result.merge(source3, on="ROW_WID", how="inner")
result = result.merge(source6, on="ROW_WID", how="inner")
result = result.merge(source7, on="ROW_WID", how="inner")
result = result.merge(source8, on="ROW_WID", how="inner")
result = result.merge(source9, on="ROW_WID", how="inner")

# Project only CANCEL_DT column as per target schema
final_result = result[["CANCEL_DT"]]

# Write output
final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)