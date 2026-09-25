import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

# UNION the tables with the same schema
union_df = pd.concat([df0, df8, df9], ignore_index=True)

# LEFT JOIN with all other tables on ROW_WID
join_1 = pd.merge(union_df, df2, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, df4, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, df5, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, df6, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, df7, on="ROW_WID", how="left")

# Select TECHSUPPORT_NUM, drop nulls and duplicates
result = join_6[["TECHSUPPORT_NUM"]].copy()
result = result[result["TECHSUPPORT_NUM"].notna()]
result = result.drop_duplicates()

# Convert to integer type
result["TECHSUPPORT_NUM"] = result["TECHSUPPORT_NUM"].astype("Int64")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)