import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)

union_df = pd.concat([df0, df1, df8, df9], ignore_index=True)
merged_df = pd.merge(union_df, df4, on="ROW_WID", how="inner")
result = merged_df.groupby("TECHSUPPORT_NUM", as_index=False).size()
result = result.rename(columns={"size": "count"})
final_df = merged_df[["TECHSUPPORT_NUM"]].drop_duplicates().reset_index(drop=True)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)