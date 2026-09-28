import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

agg_0 = df0.groupby('label').agg(y=('y', 'mean'), x=('x', 'count')).reset_index()
agg_1 = df1.groupby('label').agg(y=('y', 'mean'), x=('x', 'count')).reset_index()
agg_2 = df2.groupby('label').agg(y=('y', 'mean'), x=('x', 'count')).reset_index()
agg_3 = df3.groupby('label').agg(y=('y', 'mean'), x=('x', 'count')).reset_index()

result = pd.concat([agg_0, agg_1, agg_2, agg_3], ignore_index=True)

result['label'] = result['label'].astype('category').cat.codes + 1
result['x'] = result['x'].astype(int)
result['y'] = result['y'].astype(float)

result = result[['y', 'x', 'label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)