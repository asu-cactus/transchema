import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

df = s0.merge(s1, on='2012-12-05', how='outer')
df = df.merge(s2, on='2012-12-05', how='outer')
df = df.merge(s3, on='2012-12-05', how='outer')
df = df.merge(s4, on='2012-12-05', how='outer')
df = df.merge(s5, on='2012-12-05', how='outer')
df = df.merge(s6, on='2012-12-05', how='outer')
df = df.merge(s7, on='2012-12-05', how='outer')
df = df.merge(s8, on='2012-12-05', how='outer')
df = df.merge(s9, on='2012-12-05', how='outer')
df = df.merge(s10, on='2012-12-05', how='outer')

df = df.astype({
    '2012-12-05': str,
    '301.0': 'Int64',
    '0.0075805085': float,
    '0.0179': float,
    '6.9': float,
    '0.17657143': float,
    '20.3333': float,
    '0.016157143': float,
    '242.364': float,
    '0.1646': float,
    '0.7268': float,
    '0.4332': float
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)