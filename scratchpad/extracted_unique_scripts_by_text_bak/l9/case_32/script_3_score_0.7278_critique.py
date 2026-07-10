import pandas as pd

# Read all sources with index_col=0 to ignore the first numerical index column
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

# Union the tables with the same schema
union_5_6_7_8 = pd.concat([s5, s6, s7, s8], ignore_index=True)

# Join all tables on ROW_WID
join_1 = pd.merge(union_5_6_7_8, s0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s2, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s3, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s4, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="inner")

# The target schema is ['VISITS_NUM'], so select that column as is
result = join_6[["VISITS_NUM"]]

# Write the result to the target CSV file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)