import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)
union_df = pd.concat([df0, df8, df9], ignore_index=True)

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

merged = union_df.merge(df2, on="ROW_WID", how="left") \
                 .merge(df3, on="ROW_WID", how="left") \
                 .merge(df4, on="ROW_WID", how="left") \
                 .merge(df5, on="ROW_WID", how="left") \
                 .merge(df6, on="ROW_WID", how="left") \
                 .merge(df7, on="ROW_WID", how="left")

result = merged[["TECHSUPPORT_NUM"]].copy()
result["TECHSUPPORT_NUM"] = pd.to_numeric(result["TECHSUPPORT_NUM"], errors='coerce').astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)