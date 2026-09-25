import pandas as pd

# Read and union the dimension tables with identical schema
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
union_result = pd.concat([s3, s4, s7, s8], ignore_index=True)

# Read aspect tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# Join unioned dimension table with all aspect tables on ROW_WID
join_1 = pd.merge(union_result, s0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s2, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s5, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s6, on="ROW_WID", how="inner")
final_join = pd.merge(join_5, s9, on="ROW_WID", how="inner")

# Project only the target column
result = final_join[["INBOUND_CALLS_NUM"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)