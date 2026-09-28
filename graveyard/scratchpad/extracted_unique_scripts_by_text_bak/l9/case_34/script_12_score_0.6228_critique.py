import pandas as pd

# Read and union the dimension tables with identical schema
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)

union_df = pd.concat([df2, df5, df6, df8], ignore_index=True)

# Read other aspect tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# Join all tables on ROW_WID using inner joins
join_0 = pd.merge(union_df, df0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, df1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, df4, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, df7, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, df9, on="ROW_WID", how="inner")

# Extract distinct KEYWORDS_NUM values as integer to match target schema
final_result = join_5[["KEYWORDS_NUM"]].drop_duplicates().reset_index(drop=True)
final_result["KEYWORDS_NUM"] = final_result["KEYWORDS_NUM"].astype(int)

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)