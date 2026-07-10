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

union_5_6_7_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

join_1_2 = pd.merge(s1, s2, on="ROW_WID", how="inner")
join_1_2_0 = pd.merge(join_1_2, s0, on="ROW_WID", how="inner")
join_1_2_0_3 = pd.merge(join_1_2_0, s3, on="ROW_WID", how="inner")
join_1_2_0_3_4 = pd.merge(join_1_2_0_3, s4, on="ROW_WID", how="inner")
join_all = pd.merge(join_1_2_0_3_4, union_5_6_7_8, on="ROW_WID", how="inner")
join_all = pd.merge(join_all, s9, on="ROW_WID", how="inner")

result = join_all.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "count"})

final = result[["VISITS_NUM"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)