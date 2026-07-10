import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)

# UNION the four dimension tables with ARPU
dim_union = pd.concat([s3, s5, s6, s7], ignore_index=True)

# Join with s0 on ROW_WID
join_1 = pd.merge(dim_union, s0, on='ROW_WID', how='inner')

# Join with s1 on ROW_WID
join_2 = pd.merge(join_1, s1, on='ROW_WID', how='inner')

# Join with s2 on ROW_WID
join_3 = pd.merge(join_2, s2, on='ROW_WID', how='inner')

# Join with s4 on ROW_WID
join_4 = pd.merge(join_3, s4, on='ROW_WID', how='inner')

# Join with s8 on ROW_WID
join_5 = pd.merge(join_4, s8, on='ROW_WID', how='inner')

# Join with s9 on ROW_WID
join_6 = pd.merge(join_5, s9, on='ROW_WID', how='inner')

# The target schema is ['ARPU'] only
target = join_6[['ARPU']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)