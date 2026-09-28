import pandas as pd

# Read and union the dimension tables with the same schema
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
union_df = pd.concat([df5, df6, df7, df8], ignore_index=True)

# Read other source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# Join all tables on ROW_WID using inner joins
join1 = pd.merge(union_df, df0, on="ROW_WID", how="inner")
join2 = pd.merge(join1, df1, on="ROW_WID", how="inner")
join3 = pd.merge(join2, df2, on="ROW_WID", how="inner")
join4 = pd.merge(join3, df3, on="ROW_WID", how="inner")
join5 = pd.merge(join4, df4, on="ROW_WID", how="inner")
join6 = pd.merge(join5, df9, on="ROW_WID", how="inner")

# Extract VISITS_NUM column, drop NaNs, convert to int, sort and reset index
final = join6["VISITS_NUM"].dropna().astype(int).sort_values().reset_index(drop=True).to_frame()

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)