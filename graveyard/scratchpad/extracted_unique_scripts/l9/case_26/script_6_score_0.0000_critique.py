import pandas as pd

# Read dimension tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)

# Join dimension tables on ROW_WID using inner join to avoid row multiplication
join_result_1 = pd.merge(s2, s3, on="ROW_WID", how="inner", suffixes=('_2', '_3'))
join_result_2 = pd.merge(join_result_1, s4, on="ROW_WID", how="inner", suffixes=('', '_4'))
join_result_3 = pd.merge(join_result_2, s8, on="ROW_WID", how="inner", suffixes=('', '_8'))

# Read aspect tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_1.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_9.csv", index_col=0)

# Join aspect tables one by one on ROW_WID using inner join
join_result_4 = pd.merge(join_result_3, s0, on="ROW_WID", how="inner")
join_result_5 = pd.merge(join_result_4, s1, on="ROW_WID", how="inner")
join_result_6 = pd.merge(join_result_5, s5, on="ROW_WID", how="inner")
join_result_7 = pd.merge(join_result_6, s6, on="ROW_WID", how="inner")
join_result_8 = pd.merge(join_result_7, s7, on="ROW_WID", how="inner")
final_join = pd.merge(join_result_8, s9, on="ROW_WID", how="inner")

# Project CANCEL_DT column only
result = final_join[["CANCEL_DT"]].copy()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False)