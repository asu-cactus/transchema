import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_10.csv", index_col=0)

join_df = pd.merge(s3, s9, left_on='0', right_on='0', how='inner', suffixes=('_3', '_9'))
grouped = join_df.groupby('0').size().reset_index(name='count')
grouped = grouped[['0']]  # keep only the group by column '0'

# Union all other sources plus the grouped join result
union_df = pd.concat([s0, s1, s2, s4, s5, s6, s7, s8, s10, grouped], ignore_index=True)

union_df = union_df.astype({'0': 'int64'})

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_2/target_multisource_mcts.csv", index=False)