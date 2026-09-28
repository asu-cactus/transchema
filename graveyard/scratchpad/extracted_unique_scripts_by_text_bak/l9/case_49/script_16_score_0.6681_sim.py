import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_10.csv", index_col=0)
s11 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_11.csv", index_col=0)
s12 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_12.csv", index_col=0)
s13 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_13.csv", index_col=0)
s14 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/training_14.csv", index_col=0)

join_result = pd.merge(s4, s5, left_on='emp_title', right_on='emp_title', suffixes=('_4', '_5'))

union_frames = [s0, s1, s2, s3, join_result[['emp_title']], s6, s7, s8, s9, s10, s11, s12, s13, s14]
target_df = pd.concat(union_frames, ignore_index=True)

target_df = target_df[['emp_title']].astype(int)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)