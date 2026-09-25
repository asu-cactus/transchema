import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

union_3_4_7_8 = pd.concat([s3, s4, s7, s8], ignore_index=True)

join_0 = union_3_4_7_8.merge(s0, on="ROW_WID", how="outer")
join_1 = join_0.merge(s1, on="ROW_WID", how="outer")
join_2 = join_1.merge(s2, on="ROW_WID", how="outer")
join_3 = join_2.merge(s5, on="ROW_WID", how="outer")
join_4 = join_3.merge(s6, on="ROW_WID", how="outer")
join_5 = join_4.merge(s9, on="ROW_WID", how="outer")

result = join_5.groupby("INBOUND_CALLS_NUM", dropna=False).size().reset_index(name="count")

final = result[["INBOUND_CALLS_NUM"]].copy()
final["INBOUND_CALLS_NUM"] = final["INBOUND_CALLS_NUM"].astype("Int64")

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)