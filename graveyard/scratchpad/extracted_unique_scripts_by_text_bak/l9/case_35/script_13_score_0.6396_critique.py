import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# Union all four large tables with the same schema
union_df = pd.concat([df0, df1, df8, df9], ignore_index=True)

# Read aspect tables
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

# Join all aspect tables on ROW_WID
join1 = pd.merge(union_df, df2, on="ROW_WID", how="inner")
join2 = pd.merge(join1, df3, on="ROW_WID", how="inner")
join3 = pd.merge(join2, df4, on="ROW_WID", how="inner")
join4 = pd.merge(join3, df5, on="ROW_WID", how="inner")
join5 = pd.merge(join4, df6, on="ROW_WID", how="inner")
join6 = pd.merge(join5, df7, on="ROW_WID", how="inner")

# Select distinct TECHSUPPORT_NUM values only
result = join6[["TECHSUPPORT_NUM"]].drop_duplicates().reset_index(drop=True)

# Write output with exact target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)