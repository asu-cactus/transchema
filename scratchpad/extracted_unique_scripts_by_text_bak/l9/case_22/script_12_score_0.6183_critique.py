import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# UNION the dimension tables (source3, source4, source7, source8)
dim_union = pd.concat([source3, source4, source7, source8], ignore_index=True)

# Join dimension union with source0 on ROW_WID
join_0 = pd.merge(dim_union, source0, on="ROW_WID", how="inner")

# Join with source1 on ROW_WID
join_1 = pd.merge(join_0, source1, on="ROW_WID", how="inner")

# Join with source2 on ROW_WID
join_2 = pd.merge(join_1, source2, on="ROW_WID", how="inner")

# Join with source5 on ROW_WID
join_3 = pd.merge(join_2, source5, on="ROW_WID", how="inner")

# Join with source6 on ROW_WID
join_4 = pd.merge(join_3, source6, on="ROW_WID", how="inner")

# Join with source9 on ROW_WID
final_join = pd.merge(join_4, source9, on="ROW_WID", how="inner")

# Project only INBOUND_CALLS_NUM column (from source1)
# Drop duplicates to match target examples (unique INBOUND_CALLS_NUM values)
final = final_join[["INBOUND_CALLS_NUM"]].drop_duplicates().reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)