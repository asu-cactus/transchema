import pandas as pd

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
union_result = pd.concat([s3, s4, s7, s8], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, s0, on="ROW_WID", how="inner")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s1, on="ROW_WID", how="inner")

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, s2, on="ROW_WID", how="inner")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, s5, on="ROW_WID", how="inner")

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, s6, on="ROW_WID", how="inner")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="inner")

result = final_join.groupby("INBOUND_CALLS_NUM", as_index=False).size()
result.columns = ["INBOUND_CALLS_NUM", "count"]

result = result[["INBOUND_CALLS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)