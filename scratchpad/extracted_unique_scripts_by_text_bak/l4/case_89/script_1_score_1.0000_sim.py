import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_89/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_89/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_89/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)
result = df_all.groupby('video', as_index=False).size().drop(columns='size')
result = result[['video']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_89/target_multisource_mcts.csv", index=False)