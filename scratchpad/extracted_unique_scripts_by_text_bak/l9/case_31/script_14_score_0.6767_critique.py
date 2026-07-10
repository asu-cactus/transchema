import pandas as pd

# Read the four large source tables with the same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

# Union these four tables
union_df = pd.concat([df0, df1, df3, df5], ignore_index=True)

# Read the other source tables (aspect tables)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# Join unioned table with all other tables on ROW_WID using inner joins
join1 = pd.merge(union_df, df2, on="ROW_WID", how="inner")
join2 = pd.merge(join1, df4, on="ROW_WID", how="inner")
join3 = pd.merge(join2, df6, on="ROW_WID", how="inner")
join4 = pd.merge(join3, df7, on="ROW_WID", how="inner")
join5 = pd.merge(join4, df8, on="ROW_WID", how="inner")
join6 = pd.merge(join5, df9, on="ROW_WID", how="inner")

# Select distinct HOME_PASSED values as target expects only this column
result = join6[["HOME_PASSED"]].drop_duplicates().reset_index(drop=True)

# Cast HOME_PASSED to int as in target examples
result["HOME_PASSED"] = result["HOME_PASSED"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)