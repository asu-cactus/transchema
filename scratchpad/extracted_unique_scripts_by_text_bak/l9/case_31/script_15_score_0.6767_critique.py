import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# UNION the four dimension tables with the same schema
union_df = pd.concat([df0, df1, df3, df5], ignore_index=True)

# Join union_df with all aspect tables on ROW_WID
result = union_df.merge(df2, on="ROW_WID", how="inner")
result = result.merge(df4, on="ROW_WID", how="inner")
result = result.merge(df6, on="ROW_WID", how="inner")
result = result.merge(df7, on="ROW_WID", how="inner")
result = result.merge(df8, on="ROW_WID", how="inner")
result = result.merge(df9, on="ROW_WID", how="inner")

# Group by HOME_PASSED and count ROW_WID
agg_df = result.groupby("HOME_PASSED", as_index=False).agg({"ROW_WID": "count"})

# Rename count column to something else if needed, but target schema only has HOME_PASSED
# So output only HOME_PASSED column
agg_df = agg_df[["HOME_PASSED"]]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)