import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# UNION the four tables with the same schema
df_union = pd.concat([df2, df5, df6, df8], ignore_index=True)

# Join all tables on ROW_WID
df = df_union.merge(df0, on="ROW_WID", how="inner") \
             .merge(df1, on="ROW_WID", how="inner") \
             .merge(df3, on="ROW_WID", how="inner") \
             .merge(df4, on="ROW_WID", how="inner") \
             .merge(df7, on="ROW_WID", how="inner") \
             .merge(df9, on="ROW_WID", how="inner")

# Select distinct KEYWORDS_NUM as target schema only has this column
result = df[["KEYWORDS_NUM"]].drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)