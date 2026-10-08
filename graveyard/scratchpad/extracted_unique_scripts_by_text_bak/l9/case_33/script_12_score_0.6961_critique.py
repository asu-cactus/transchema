import pandas as pd

# Read dimension tables with same schema and union them
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)
union_df = pd.concat([df4, df5, df7, df9], ignore_index=True)

# Read aspect tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)

# Join unioned dimension table with aspect tables on ROW_WID using left joins to preserve all rows from union_df
join1 = pd.merge(union_df, df0, on="ROW_WID", how="left")
join2 = pd.merge(join1, df1, on="ROW_WID", how="left")
join3 = pd.merge(join2, df2, on="ROW_WID", how="left")
join4 = pd.merge(join3, df3, on="ROW_WID", how="left")
join5 = pd.merge(join4, df6, on="ROW_WID", how="left")
final_join = pd.merge(join5, df8, on="ROW_WID", how="left")

# Select INTERACTIONS_NUM, drop rows with NaN in INTERACTIONS_NUM, convert to int
result = final_join[["INTERACTIONS_NUM"]].dropna(subset=["INTERACTIONS_NUM"]).copy()
result["INTERACTIONS_NUM"] = result["INTERACTIONS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)