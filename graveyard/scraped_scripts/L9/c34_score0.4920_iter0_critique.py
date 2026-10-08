import pandas as pd

# Read and union the four large tables with the same schema
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
union_df = pd.concat([s2, s5, s6, s8], ignore_index=True)

# Read other source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# Perform left joins starting from union_df to keep all rows from union_df
join_0 = pd.merge(union_df, s0, on="ROW_WID", how="left")
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s7, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s9, on="ROW_WID", how="left")

# Select distinct KEYWORDS_NUM values, dropping rows where KEYWORDS_NUM is NaN
result = join_5[["KEYWORDS_NUM"]].dropna().drop_duplicates().sort_values("KEYWORDS_NUM").reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)