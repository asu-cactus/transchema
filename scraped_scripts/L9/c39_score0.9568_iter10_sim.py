import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_9.csv", index_col=0)
df10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_39/training_10.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4, df5, df6, df7, df8, df9, df10], axis=1)
df_all.columns = [f"source_{i}" for i in range(len(df_all.columns))]

df_unpivot = df_all.melt(value_name='0')[['0']]
df_unpivot['0'] = df_unpivot['0'].astype('Int64')

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length9_39/target_multisource_mcts.csv", index=False)