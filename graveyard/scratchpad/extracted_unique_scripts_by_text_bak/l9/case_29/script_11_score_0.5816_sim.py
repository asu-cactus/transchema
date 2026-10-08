import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

join_0_1 = pd.merge(s0, s1, on="ROW_WID", how="inner")

union_2_5_6_9 = pd.concat([s2, s5, s6, s9], ignore_index=True)

join_0_1_2_5_6_9 = pd.merge(join_0_1, union_2_5_6_9, on="ROW_WID", how="inner", suffixes=('', '_dup'))
dup_cols = [c for c in join_0_1_2_5_6_9.columns if c.endswith('_dup')]
join_0_1_2_5_6_9.drop(columns=dup_cols, inplace=True)

join_0_1_2_5_6_9_3 = pd.merge(join_0_1_2_5_6_9, s3, on="ROW_WID", how="inner")
join_0_1_2_5_6_9_3_4 = pd.merge(join_0_1_2_5_6_9_3, s4, on="ROW_WID", how="inner")
join_0_1_2_5_6_9_3_4_7 = pd.merge(join_0_1_2_5_6_9_3_4, s7, on="ROW_WID", how="inner")
final_join = pd.merge(join_0_1_2_5_6_9_3_4_7, s8, on="ROW_WID", how="inner")

result = final_join.groupby("COLLECTION_EVENTS_NUM", as_index=False).size()
result.rename(columns={"size": "COLLECTION_EVENTS_NUM"}, inplace=True)
result = result[["COLLECTION_EVENTS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)