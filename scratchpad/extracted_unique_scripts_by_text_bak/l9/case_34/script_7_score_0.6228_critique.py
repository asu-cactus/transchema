import pandas as pd

# Read dimension tables with same schema
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)

# Union dimension tables
unioned_dim = pd.concat([df2, df5, df6, df8], ignore_index=True)

# Read aspect tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# Join unioned dimension table with all aspect tables on ROW_WID using inner joins
join_0 = pd.merge(unioned_dim, df0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, df1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, df4, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, df7, on="ROW_WID", how="inner")
final_join = pd.merge(join_4, df9, on="ROW_WID", how="inner")

# Select KEYWORDS_NUM column and drop duplicates to match target row count
result = final_join[["KEYWORDS_NUM"]].copy()
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype(int)
result = result.drop_duplicates()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)