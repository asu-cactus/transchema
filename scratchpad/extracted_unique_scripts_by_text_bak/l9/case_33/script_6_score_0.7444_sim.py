import pandas as pd

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)
union_df = pd.concat([df4, df5, df7, df9], ignore_index=True)

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
join1 = pd.merge(union_df, df0, on="ROW_WID", how="inner")

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
join2 = pd.merge(join1, df1, on="ROW_WID", how="inner")

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
join3 = pd.merge(join2, df2, on="ROW_WID", how="inner")

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
join4 = pd.merge(join3, df3, on="ROW_WID", how="inner")

df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
join5 = pd.merge(join4, df6, on="ROW_WID", how="inner")

df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
final_join = pd.merge(join5, df8, on="ROW_WID", how="inner")

result = final_join[["INTERACTIONS_NUM"]].copy()
result["INTERACTIONS_NUM"] = result["INTERACTIONS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)