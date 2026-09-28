import pandas as pd

# Read and union the four source tables with the same schema
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)
union_result = pd.concat([s3, s5, s6, s7], ignore_index=True)

# Read other source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)

# Join all on ROW_WID
df = pd.merge(union_result, s0, on="ROW_WID", how="inner")
df = pd.merge(df, s1, on="ROW_WID", how="inner")
df = pd.merge(df, s2, on="ROW_WID", how="inner")
df = pd.merge(df, s4, on="ROW_WID", how="inner")
df = pd.merge(df, s8, on="ROW_WID", how="inner")
df = pd.merge(df, s9, on="ROW_WID", how="inner")

# Project only ARPU column as in target schema
result = df[["ARPU"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)