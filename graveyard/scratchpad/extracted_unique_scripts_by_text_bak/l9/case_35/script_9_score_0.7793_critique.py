import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)

# Union the four large tables with the same schema
union_df = pd.concat([s0, s1, s8, s9], ignore_index=True)

# Read aspect tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv", index_col=0)

# Join unioned table with all aspect tables on ROW_WID using inner joins
join_1 = pd.merge(union_df, s2, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s3, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s5, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s6, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s7, on="ROW_WID", how="inner")

# Project only the TECHSUPPORT_NUM column as in the target schema
output_df = join_6[["TECHSUPPORT_NUM"]]

# Write output to the specified path without index
output_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)