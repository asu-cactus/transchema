import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_10.csv", index_col=0)
s11 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_11.csv", index_col=0)
s12 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_12.csv", index_col=0)
s13 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_13.csv", index_col=0)
s14 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_14.csv", index_col=0)

join = pd.merge(s1, s12, left_on='title', right_on='title', suffixes=('_1', '_12'))

# UNPIVOT the join result: since both columns are 'title_1' and 'title_12', unpivot to one column 'title'
unpivoted = pd.melt(join, value_vars=['title_1', 'title_12'], value_name='title')
unpivoted = unpivoted[['title']]

# Union all sources with the unpivoted join result
all_frames = [s0, unpivoted, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s13, s14]
result = pd.concat(all_frames, ignore_index=True)

result = result[['title']].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_51/target_multisource_mcts.csv", index=False)