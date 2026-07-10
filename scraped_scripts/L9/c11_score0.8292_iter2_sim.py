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

df['2012-12-05'] = df['2012-12-05'].astype(str)
df['301.0'] = pd.to_numeric(df['301.0'], errors='coerce').astype('Int64')
float_cols = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']
for col in float_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)