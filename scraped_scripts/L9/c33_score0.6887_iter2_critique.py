import pandas as pd

# Read all sources with index_col=0 to ignore the first numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

# UNION dimension tables (sources 4,5,7,9) with identical schema
union_dim = pd.concat([source4, source5, source7, source9], ignore_index=True)

# Join unioned dimension table with aspect tables on ROW_WID
join_0 = pd.merge(union_dim, source0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, source1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, source2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, source3, on="ROW_WID", how="inner")
join_6 = pd.merge(join_3, source6, on="ROW_WID", how="inner")
join_8 = pd.merge(join_6, source8, on="ROW_WID", how="inner")

# Project the target column INTERACTIONS_NUM
result = join_8[["INTERACTIONS_NUM"]].copy()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)