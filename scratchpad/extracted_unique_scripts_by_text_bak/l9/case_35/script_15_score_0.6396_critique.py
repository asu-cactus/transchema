import pandas as pd

# Read the source tables with the same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# Union the four tables with the same schema
union_df = pd.concat([df0, df1, df8, df9], ignore_index=True)

# Read the other source tables (aspect tables)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

# Join all tables on ROW_WID using inner joins
merged = union_df.merge(df2, on="ROW_WID", how="inner")\
                 .merge(df3, on="ROW_WID", how="inner")\
                 .merge(df4, on="ROW_WID", how="inner")\
                 .merge(df5, on="ROW_WID", how="inner")\
                 .merge(df6, on="ROW_WID", how="inner")\
                 .merge(df7, on="ROW_WID", how="inner")

# Select distinct TECHSUPPORT_NUM values
final_df = merged[["TECHSUPPORT_NUM"]].drop_duplicates().reset_index(drop=True)

# Write the final output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)