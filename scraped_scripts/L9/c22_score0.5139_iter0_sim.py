import pandas as pd

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
union_3_4_7_8 = pd.concat([src3, src4, src7, src8], ignore_index=True)

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
join_0 = pd.merge(union_3_4_7_8, src0, on="ROW_WID", how="inner")

src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
join_1 = pd.merge(join_0, src1, on="ROW_WID", how="inner")

src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
join_2 = pd.merge(join_1, src2, on="ROW_WID", how="inner")

src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
join_3 = pd.merge(join_2, src5, on="ROW_WID", how="inner")

src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
join_4 = pd.merge(join_3, src6, on="ROW_WID", how="inner")

src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)
join_5 = pd.merge(join_4, src9, on="ROW_WID", how="inner")

result = join_5.groupby("INBOUND_CALLS_NUM", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires INBOUND_CALLS_NUM column, so we keep only that column.
# The target examples show only INBOUND_CALLS_NUM column, so we drop the count column.
# But the partial plan says GROUP_BY : [INBOUND_CALLS_NUM], so the output is grouped by INBOUND_CALLS_NUM.
# The target examples show counts of rows per INBOUND_CALLS_NUM, but the target schema only has INBOUND_CALLS_NUM column.
# So we output unique INBOUND_CALLS_NUM values (group keys) only.

final_result = result[["INBOUND_CALLS_NUM"]]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)