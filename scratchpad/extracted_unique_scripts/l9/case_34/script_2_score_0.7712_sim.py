import pandas as pd

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)

union_df = pd.concat([df2, df5, df6, df8], ignore_index=True)

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
join_0 = pd.merge(union_df, df0, on="ROW_WID", how="inner")

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
join_1 = pd.merge(join_0, df1, on="ROW_WID", how="inner")

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="inner")

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
join_3 = pd.merge(join_2, df4, on="ROW_WID", how="inner")

df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
join_4 = pd.merge(join_3, df7, on="ROW_WID", how="inner")

df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)
final_join = pd.merge(join_4, df9, on="ROW_WID", how="inner")

result = final_join[["KEYWORDS_NUM"]].copy()
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)