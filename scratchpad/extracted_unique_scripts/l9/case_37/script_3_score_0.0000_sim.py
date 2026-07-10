import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_10.csv", index_col=0)

df = s0.merge(s1, left_on='0', right_on='0', suffixes=('_0', '_1'))
df = df.merge(s2, on='0')
df = df.merge(s3, on='0', suffixes=('', '_3'))
df = df.merge(s4, on='0', suffixes=('', '_4'))
df = df.merge(s5, on='0', suffixes=('', '_5'))
df = df.merge(s6, on='0', suffixes=('', '_6'))
df = df.merge(s7, on='0', suffixes=('', '_7'))
df = df.merge(s8, on='0', suffixes=('', '_8'))
df = df.merge(s9, on='0', suffixes=('', '_9'))
df = df.merge(s10, on='0', suffixes=('', '_10'))

cols = [c for c in df.columns if c != '0']
df['0'] = df[cols].sum(axis=1).astype(int)

result = df[['0']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_37/target_multisource_mcts.csv")