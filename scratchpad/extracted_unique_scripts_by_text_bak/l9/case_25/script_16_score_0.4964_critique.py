import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# UNION the four source tables with the same schema
unioned = pd.concat([s0, s1, s4, s5], ignore_index=True)

# Join unioned with other source tables on ROW_WID using left outer joins to keep all rows from unioned
result = unioned.merge(s2, on="ROW_WID", how="left")
result = result.merge(s3, on="ROW_WID", how="left")
result = result.merge(s6, on="ROW_WID", how="left")
result = result.merge(s7, on="ROW_WID", how="left")
result = result.merge(s8, on="ROW_WID", how="left")
result = result.merge(s9, on="ROW_WID", how="left")

# Project only CANCEL_DT column as per target schema
output = result[["CANCEL_DT"]]

# Write output to CSV
output.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)