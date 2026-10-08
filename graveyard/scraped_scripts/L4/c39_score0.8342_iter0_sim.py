import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_39/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_39/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_39/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

grouped = df.groupby('label', as_index=False).agg({'x':'count', 'y':'count'})

grouped['x'] = 20
grouped['y'] = 20

grouped = grouped[['label', 'x', 'y']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_39/target_multisource_mcts.csv", index=False)