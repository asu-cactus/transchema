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

join_0_1 = pd.merge(s0, s1, on="ROW_WID", how="inner")
join_0_1_2 = pd.merge(join_0_1, s2, on="ROW_WID", how="inner")
join_0_1_2_3 = pd.merge(join_0_1_2, s3, on="ROW_WID", how="inner")

union_4_5 = pd.concat([s4, s5], ignore_index=True)
union_4_5_7 = pd.concat([union_4_5, s7], ignore_index=True)
union_4_5_7_9 = pd.concat([union_4_5_7, s9], ignore_index=True)

join_0_1_2_3_4 = pd.merge(join_0_1_2_3, union_4_5_7_9, on="ROW_WID", how="inner")
join_0_1_2_3_4_6 = pd.merge(join_0_1_2_3_4, s6, on="ROW_WID", how="inner")
join_0_1_2_3_4_6_8 = pd.merge(join_0_1_2_3_4_6, s8, on="ROW_WID", how="inner")

result = join_0_1_2_3_4_6_8.groupby("INTERACTIONS_NUM", as_index=False).size()
result.columns = ["INTERACTIONS_NUM", "count"]

result = result[["INTERACTIONS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)