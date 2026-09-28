import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)
union_result = pd.concat([s2, s3, s4, s8], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, s0, on="ROW_WID", how="left")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_1.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s1, on="ROW_WID", how="left")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_5.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, s5, on="ROW_WID", how="left")

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_6.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, s6, on="ROW_WID", how="left")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_7.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, s7, on="ROW_WID", how="left")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_9.csv", index_col=0)
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="left")

result = final_join[["CANCEL_DT"]].copy()
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False)