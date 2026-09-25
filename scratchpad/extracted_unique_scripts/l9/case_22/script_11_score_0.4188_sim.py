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

# Merge all sources on ROW_WID
merged = df_3_4_7_8.merge(df0, on="ROW_WID", how="outer") \
                  .merge(df1, on="ROW_WID", how="outer") \
                  .merge(df2, on="ROW_WID", how="outer") \
                  .merge(df5, on="ROW_WID", how="outer") \
                  .merge(df6, on="ROW_WID", how="outer") \
                  .merge(df9, on="ROW_WID", how="outer")

# The target only requires INBOUND_CALLS_NUM column
# Group by INBOUND_CALLS_NUM to count occurrences (pivot + group_by)
result = merged.groupby("INBOUND_CALLS_NUM", dropna=False).size().reset_index(name="count")

# The target schema is ['INBOUND_CALLS_NUM'] with integer values
# The target examples show just the INBOUND_CALLS_NUM column, so we output that column repeated by count times
# To produce the target table with 4161 rows, replicate INBOUND_CALLS_NUM by count
final = result.loc[result.index.repeat(result['count'])].reset_index(drop=True)[["INBOUND_CALLS_NUM"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)