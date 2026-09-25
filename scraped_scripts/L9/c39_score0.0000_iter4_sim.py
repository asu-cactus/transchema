import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_10.csv", index_col=0)

df = s0.merge(s1, left_on='0', right_on='0', how='inner', suffixes=('', '_1'))
df = df.merge(s2, left_on='0', right_on='0', how='inner')
df = df.merge(s3, left_on='0', right_on='0', how='inner', suffixes=('', '_3'))
df = df.merge(s4, left_on='0', right_on='0', how='inner', suffixes=('', '_4'))
df = df.merge(s5, left_on='0', right_on='0', how='inner', suffixes=('', '_5'))
df = df.merge(s6, left_on='0', right_on='0', how='inner', suffixes=('', '_6'))
df = df.merge(s7, left_on='0', right_on='0', how='inner', suffixes=('', '_7'))
df = df.merge(s8, left_on='0', right_on='0', how='inner', suffixes=('', '_8'))
df = df.merge(s9, left_on='0', right_on='0', how='inner', suffixes=('', '_9'))
df = df.merge(s10, left_on='0', right_on='0', how='inner', suffixes=('', '_10'))

cols_to_sum = [col for col in df.columns if col != '0']
df['0'] = df['0'].astype(int)
df[cols_to_sum] = df[cols_to_sum].fillna(0).astype(int)
df['0'] = df[cols_to_sum].sum(axis=1)

df = df[['0']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_39/target_multisource_mcts.csv")