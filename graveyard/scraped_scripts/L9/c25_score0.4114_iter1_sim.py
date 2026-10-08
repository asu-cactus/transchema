import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

union_df = pd.concat([df0, df4, df5], ignore_index=True)

join_1 = pd.merge(union_df, df2, on="ROW_WID", how="left")
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, df6, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, df7, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, df8, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, df9, on="ROW_WID", how="left")

result = join_6[["CANCEL_DT"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)