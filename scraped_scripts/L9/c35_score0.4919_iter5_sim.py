import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

union_df = pd.concat([s0, s1, s8, s9], ignore_index=True)

joined = pd.merge(union_df, s4, on="ROW_WID", how="inner")

result = joined.groupby("TECHSUPPORT_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires TECHSUPPORT_NUM column, so we keep only that column.
# The target examples show only TECHSUPPORT_NUM column, so we drop the count column.
final = result[["TECHSUPPORT_NUM"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)