import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# Union the sources with identical schema (sources 3,4,7,8)
df_3_4_7_8 = pd.concat([df3, df4, df7, df8], ignore_index=True)

# Join all sources on ROW_WID
merged = df_3_4_7_8.merge(df0, on="ROW_WID", how="inner") \
                  .merge(df1, on="ROW_WID", how="inner") \
                  .merge(df2, on="ROW_WID", how="inner") \
                  .merge(df5, on="ROW_WID", how="inner") \
                  .merge(df6, on="ROW_WID", how="inner") \
                  .merge(df9, on="ROW_WID", how="inner")

# Group by ROW_WID and sum INBOUND_CALLS_NUM
result = merged.groupby("ROW_WID", dropna=False)["INBOUND_CALLS_NUM"].sum().reset_index()

# Project only INBOUND_CALLS_NUM column as per target schema
final = result[["INBOUND_CALLS_NUM"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)