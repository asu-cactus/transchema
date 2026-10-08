import pandas as pd

# Read all source files with index_col=0 as instructed
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# UNION the 4 tables with the same schema
union_df = pd.concat([df0, df1, df3, df5], ignore_index=True)

# Join with all other tables on ROW_WID using inner join
join_1 = pd.merge(union_df, df2, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, df4, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, df6, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, df7, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, df8, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, df9, on="ROW_WID", how="inner")

# Select only HOME_PASSED column and drop duplicates to match target tuples count
result = join_6[["HOME_PASSED"]].drop_duplicates().reset_index(drop=True)

# Write output with exact column name and no index
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)