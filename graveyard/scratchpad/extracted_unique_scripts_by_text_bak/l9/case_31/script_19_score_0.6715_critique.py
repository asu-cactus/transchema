import pandas as pd

# Read the four large tables with the same schema
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

# Union the four large tables
union_df = pd.concat([s0, s1, s3, s5], ignore_index=True)

# Read aspect tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# Join with aspect tables on ROW_WID using left joins
join_1 = pd.merge(union_df, s2, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, s4, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s6, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s7, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="left")
final_join = pd.merge(join_5, s9, on="ROW_WID", how="left")

# Select HOME_PASSED and drop duplicates to match target row count
result = final_join[["HOME_PASSED"]].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)