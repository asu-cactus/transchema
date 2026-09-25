import pandas as pd

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

union_df = pd.concat([s3, s4, s5, s7], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
join_0 = pd.merge(union_df, s0, on="ROW_WID", how="left")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="left")

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
join_2 = pd.merge(join_1, s2, on="ROW_WID", how="left")

s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
join_3 = pd.merge(join_2, s6, on="ROW_WID", how="left")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
join_4 = pd.merge(join_3, s8, on="ROW_WID", how="left")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)
join_5 = pd.merge(join_4, s9, on="ROW_WID", how="left")

result = join_5[["ARPU"]].copy()
result["ARPU"] = pd.to_numeric(result["ARPU"], errors="coerce")

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv")