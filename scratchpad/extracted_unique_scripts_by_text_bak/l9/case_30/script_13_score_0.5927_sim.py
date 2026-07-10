import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

union_result = pd.concat([s3, s4, s5, s7], ignore_index=True)

join_result_1 = pd.merge(union_result, s0, on="ROW_WID", how="inner")
join_result_2 = pd.merge(join_result_1, s1, on="ROW_WID", how="inner")
join_result_3 = pd.merge(join_result_2, s2, on="ROW_WID", how="inner")
join_result_4 = pd.merge(join_result_3, s6, on="ROW_WID", how="inner")
join_result_5 = pd.merge(join_result_4, s8, on="ROW_WID", how="inner")
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="inner")

result = final_join.groupby("ARPU", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires 'ARPU' column as float, so we keep only ARPU
result = result[["ARPU"]]
result["ARPU"] = result["ARPU"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)