import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# UNION the tables with the same schema
union_df = pd.concat([df0, df4, df5], ignore_index=True)

# JOIN all aspect tables on ROW_WID with left joins
join_1 = pd.merge(union_df, df2, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, df6, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, df7, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, df8, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, df9, on="ROW_WID", how="left")

# GROUP BY CANCEL_DT to get unique CANCEL_DT values including NaN
# Grouping by CANCEL_DT will drop NaN, so we handle NaN separately
# Extract rows with NaN CANCEL_DT
nan_cancel_dt = join_6[join_6["CANCEL_DT"].isna()][["CANCEL_DT"]].drop_duplicates()

# Extract rows with non-NaN CANCEL_DT and drop duplicates
non_nan_cancel_dt = join_6[join_6["CANCEL_DT"].notna()][["CANCEL_DT"]].drop_duplicates()

# Concatenate back to keep NaN rows as well
result = pd.concat([non_nan_cancel_dt, nan_cancel_dt], ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)