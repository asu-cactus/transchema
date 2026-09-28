import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)

# UNION the dimension tables with the same schema
unioned_dim = pd.concat([s5, s6, s8], ignore_index=True)

# JOIN unioned_dim with all aspect tables on ROW_WID using inner joins
df = unioned_dim.merge(s0, on="ROW_WID", how="inner")
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s3, on="ROW_WID", how="inner")
df = df.merge(s4, on="ROW_WID", how="inner")
df = df.merge(s7, on="ROW_WID", how="inner")
df = df.merge(s9, on="ROW_WID", how="inner")

# The target schema only requires KEYWORDS_NUM column
final_result = df[["KEYWORDS_NUM"]]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)