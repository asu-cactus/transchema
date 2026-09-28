import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

result = df4.groupby('Profit', dropna=False).size().reset_index(name='count')
result = result[['Profit']].copy()
result['Profit'] = result['Profit'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)