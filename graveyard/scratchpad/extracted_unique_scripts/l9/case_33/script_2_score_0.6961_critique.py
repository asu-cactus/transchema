import pandas as pd

# Read all sources
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

# UNION dimension tables with same schema
union_dim = pd.concat([s4, s5, s7, s9], ignore_index=True)

# JOIN union_dim with s8 (INTERACTIONS_NUM) on ROW_WID using inner join to keep only rows with INTERACTIONS_NUM
join_1 = pd.merge(union_dim, s8, on="ROW_WID", how="inner")

# LEFT JOIN with other aspect tables to keep all rows from join_1 and add other info if available
join_2 = pd.merge(join_1, s0, on="ROW_WID", how="left")
join_3 = pd.merge(join_2, s1, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s2, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s3, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, s6, on="ROW_WID", how="left")

# Project only INTERACTIONS_NUM as target schema
result = join_6[["INTERACTIONS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)