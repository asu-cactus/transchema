import pandas as pd

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)
union_result = pd.concat([df2, df5, df6, df9], ignore_index=True)

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, df0, on="ROW_WID", how="inner")

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, df1, on="ROW_WID", how="inner")

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, df3, on="ROW_WID", how="inner")

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, df4, on="ROW_WID", how="inner")

df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, df7, on="ROW_WID", how="inner")

df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
final_join = pd.merge(join_result_5, df8, on="ROW_WID", how="inner")

result = final_join[["COLLECTION_EVENTS_NUM"]].copy()
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)