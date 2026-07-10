import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_10/training_9.csv", index_col=0)

join_cols = ['admit', 'gre', 'gpa', 'prestige']
join_result = pd.merge(df0, df3, on=join_cols, how='inner')

union_frames = [df1, df2, df4, df5, df6, df7, df8, df9, join_result]
target_df = pd.concat(union_frames, ignore_index=True)

target_df = target_df.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_10/target_multisource_mcts.csv", index=False)