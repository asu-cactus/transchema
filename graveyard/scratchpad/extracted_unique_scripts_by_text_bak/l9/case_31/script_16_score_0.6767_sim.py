import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

union_result = pd.concat([s0, s1, s3, s5], ignore_index=True)

join_result_1 = pd.merge(union_result, s2, on="ROW_WID", how="inner")
join_result_2 = pd.merge(join_result_1, s4, on="ROW_WID", how="inner")
join_result_3 = pd.merge(join_result_2, s6, on="ROW_WID", how="inner")
join_result_4 = pd.merge(join_result_3, s7, on="ROW_WID", how="inner")
join_result_5 = pd.merge(join_result_4, s8, on="ROW_WID", how="inner")
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="inner")

result = final_join.groupby("HOME_PASSED", as_index=False).size()
result = result.rename(columns={"HOME_PASSED": "HOME_PASSED", "size": "HOME_PASSED"})

result = result[["HOME_PASSED"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)