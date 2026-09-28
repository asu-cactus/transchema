import pandas as pd

# Read dimension tables with same schema
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)

# Union dimension tables
union_df = pd.concat([s0, s1, s4, s5], ignore_index=True)

# Read aspect tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# Join unioned dimension table with all aspect tables on ROW_WID using left join to preserve all rows
join_1 = pd.merge(union_df, s2, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s6, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s7, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="left")

# Project CANCEL_DT column
result = join_6[["CANCEL_DT"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)