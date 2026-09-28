import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv", index_col=0)

df = s0.merge(s1, on='2012-12-05', how='inner')
df = df.merge(s2, on='2012-12-05', how='inner')
df = df.merge(s3, on='2012-12-05', how='inner')
df = df.merge(s4, on='2012-12-05', how='inner')
df = df.merge(s5, on='2012-12-05', how='inner')
df = df.merge(s6, on='2012-12-05', how='inner')
df = df.merge(s7, on='2012-12-05', how='inner')
df = df.merge(s8, on='2012-12-05', how='inner')
df = df.merge(s9, on='2012-12-05', how='inner')

df['301.0'] = df['301.0'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)