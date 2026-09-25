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

s4_5_joined = pd.merge(s4, s5, on="ROW_WID", suffixes=('_4', '_5'))
s4_5_union = pd.concat([s4_5_joined, s7, s9], ignore_index=True, sort=False)

joined_4_5_7_9 = s4_5_union

joined_0 = pd.merge(joined_4_5_7_9, s0, on="ROW_WID", how="inner")
joined_1 = pd.merge(joined_0, s1, on="ROW_WID", how="inner")
joined_2 = pd.merge(joined_1, s2, on="ROW_WID", how="inner")
joined_3 = pd.merge(joined_2, s3, on="ROW_WID", how="inner")
joined_6 = pd.merge(joined_3, s6, on="ROW_WID", how="inner")
final_join = pd.merge(joined_6, s8, on="ROW_WID", how="inner")

result = final_join[["INTERACTIONS_NUM"]].copy()
result["INTERACTIONS_NUM"] = result["INTERACTIONS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)