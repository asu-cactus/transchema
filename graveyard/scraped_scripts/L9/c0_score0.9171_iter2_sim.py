import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_0/training_10.csv", index_col=0)

joined_5_6 = pd.merge(s5, s6, left_on='0', right_on='0', suffixes=('_5', '_6'))
grouped = joined_5_6.groupby('0').size().reset_index(name='count')

union_rest = pd.concat([s0, s1, s2, s3, s4, s7, s8, s9, s10], ignore_index=True)

result = pd.concat([grouped[['0']], union_rest], ignore_index=True)

result = result.astype({'0': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_0/target_multisource_mcts.csv", index=False)