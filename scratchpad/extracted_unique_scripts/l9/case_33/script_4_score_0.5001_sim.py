import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

j1 = pd.merge(s0, s1, on="ROW_WID", how="inner")
j2 = pd.merge(j1, s2, on="ROW_WID", how="inner")
j3 = pd.merge(j2, s3, on="ROW_WID", how="inner")
j4 = pd.merge(j3, s6, on="ROW_WID", how="inner")
j5 = pd.merge(j4, s8, on="ROW_WID", how="inner")

union_4_5_7_9 = pd.concat([s4, s5, s7, s9], ignore_index=True)

final_join = pd.merge(j5, union_4_5_7_9, on="ROW_WID", how="inner")

result = final_join[["INTERACTIONS_NUM"]].sum().to_frame().T
result["INTERACTIONS_NUM"] = final_join["INTERACTIONS_NUM"].sum()
result = result[["INTERACTIONS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)