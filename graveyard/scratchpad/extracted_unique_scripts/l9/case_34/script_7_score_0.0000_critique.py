import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

# Join the four tables with the same schema on ROW_WID
join_1 = pd.merge(s2, s5, on="ROW_WID", how="inner", suffixes=('_2', '_5'))
join_2 = pd.merge(join_1, s6, on="ROW_WID", how="inner", suffixes=('', '_6'))
join_3 = pd.merge(join_2, s8, on="ROW_WID", how="inner", suffixes=('', '_8'))

# Join with other tables on ROW_WID
join_4 = pd.merge(join_3, s0, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s1, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s3, on="ROW_WID", how="inner")
join_7 = pd.merge(join_6, s4, on="ROW_WID", how="inner")
join_8 = pd.merge(join_7, s7, on="ROW_WID", how="inner")
join_9 = pd.merge(join_8, s9, on="ROW_WID", how="inner")

# Select only the KEYWORDS_NUM column as per target schema
result = join_9[["KEYWORDS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)