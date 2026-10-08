import pandas as pd

# Read all source tables with index_col=0
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# UNION all tables with the same schema (s0, s1, s8, s9)
union_0 = pd.concat([s0, s1, s8, s9], ignore_index=True)

# JOIN union_0 with all other aspect tables on ROW_WID using inner joins
result = union_0.merge(s2, on='ROW_WID', how='inner')
result = result.merge(s3, on='ROW_WID', how='inner')
result = result.merge(s4, on='ROW_WID', how='inner')
result = result.merge(s5, on='ROW_WID', how='inner')
result = result.merge(s6, on='ROW_WID', how='inner')
result = result.merge(s7, on='ROW_WID', how='inner')

# Project only TECHSUPPORT_NUM column from s4 (now in result)
output = result[['TECHSUPPORT_NUM']].copy()

# Write output
output.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)