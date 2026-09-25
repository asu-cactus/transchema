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

# Join all dimension tables on ROW_WID
df = s2.merge(s5, on="ROW_WID", how="inner", suffixes=('_2', '_5'))
df = df.merge(s6, on="ROW_WID", how="inner", suffixes=('', '_6'))
df = df.merge(s8, on="ROW_WID", how="inner", suffixes=('', '_8'))

# Join with all aspect tables on ROW_WID
df = df.merge(s0, on="ROW_WID", how="inner")
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s3, on="ROW_WID", how="inner")
df = df.merge(s4, on="ROW_WID", how="inner")
df = df.merge(s7, on="ROW_WID", how="inner")
df = df.merge(s9, on="ROW_WID", how="inner")

# Project only the target column KEYWORDS_NUM from s9
result = df[["KEYWORDS_NUM"]].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)