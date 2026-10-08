import pandas as pd

df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
union_df = pd.concat([df5, df6, df7, df8], ignore_index=True)

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
join1 = pd.merge(union_df, df0, on="ROW_WID", how="inner")

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
join2 = pd.merge(join1, df1, on="ROW_WID", how="inner")

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
join3 = pd.merge(join2, df2, on="ROW_WID", how="inner")

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
join4 = pd.merge(join3, df3, on="ROW_WID", how="inner")

df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
join5 = pd.merge(join4, df4, on="ROW_WID", how="inner")

df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)
join6 = pd.merge(join5, df9, on="ROW_WID", how="inner")

result = join6.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "VISITS_NUM"})

# The target schema is ['VISITS_NUM': integer], but the target examples show VISITS_NUM as the grouped value, not count.
# The partial plan says GROUP_BY : [VISITS_NUM], so the output is the distinct VISITS_NUM values.
# So we just output the distinct VISITS_NUM values as integers.

final = pd.DataFrame({"VISITS_NUM": join6["VISITS_NUM"].dropna().astype(int).unique()})
final = final.sort_values("VISITS_NUM").reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)