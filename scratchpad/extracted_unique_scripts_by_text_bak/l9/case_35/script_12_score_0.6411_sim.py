import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

union_df = pd.concat([df0, df8, df9], ignore_index=True)

join_1 = pd.merge(union_df, df2, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, df3, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, df4, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, df5, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, df6, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, df7, on="ROW_WID", how="inner")

result = join_6.groupby("TECHSUPPORT_NUM", as_index=False).size().rename(columns={"size": "TECHSUPPORT_NUM"})

# The groupby size counts rows per TECHSUPPORT_NUM, but target schema expects TECHSUPPORT_NUM as integer values, not counts.
# Instead, we just need distinct TECHSUPPORT_NUM values from the joined data.
# So correct approach: group by TECHSUPPORT_NUM and count distinct ROW_WID or just get unique TECHSUPPORT_NUM values.

# Correcting:
result = join_6[["TECHSUPPORT_NUM"]].drop_duplicates().reset_index(drop=True)
result["TECHSUPPORT_NUM"] = result["TECHSUPPORT_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)