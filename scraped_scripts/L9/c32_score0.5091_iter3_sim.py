import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

join_01 = pd.merge(s1, s0, on="ROW_WID", how="inner")
join_012 = pd.merge(join_01, s2, on="ROW_WID", how="inner")
join_0123 = pd.merge(join_012, s3, on="ROW_WID", how="inner")
join_01234 = pd.merge(join_0123, s4, on="ROW_WID", how="inner")

union_5678 = pd.concat([s5, s6, s7, s8], ignore_index=True)

join_012345678 = pd.merge(join_01234, union_5678, on="ROW_WID", how="inner")
final_join = pd.merge(join_012345678, s9, on="ROW_WID", how="inner")

result = final_join.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "count"})

output = result[["VISITS_NUM"]]

output.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)