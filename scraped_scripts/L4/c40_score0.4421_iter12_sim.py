import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

df0_grouped = df0.groupby('label', as_index=False).agg({'x':'sum', 'y':'sum'})
df1_grouped = df1.groupby('label', as_index=False).agg({'x':'sum', 'y':'sum'})
df2_grouped = df2.groupby('label', as_index=False).agg({'x':'sum', 'y':'sum'})
df3_grouped = df3.groupby('label', as_index=False).agg({'x':'sum', 'y':'sum'})

merged = pd.merge(df0_grouped, df1_grouped, on='label', how='outer', suffixes=('_0', '_1'))
merged = pd.merge(merged, df2_grouped, on='label', how='outer')
merged = pd.merge(merged, df3_grouped, on='label', how='outer', suffixes=('_2', '_3'))

merged = merged.rename(columns={
    'x': 'x_2',
    'y': 'y_2',
    'x_0': 'x_0',
    'y_0': 'y_0',
    'x_1': 'x_1',
    'y_1': 'y_1',
    'x_3': 'x_3',
    'y_3': 'y_3'
})

merged['x'] = merged[['x_0', 'x_1', 'x_2', 'x_3']].sum(axis=1)
merged['y'] = merged[['y_0', 'y_1', 'y_2', 'y_3']].sum(axis=1)

merged['label'] = merged['label'].astype('category').cat.codes + 1
merged['y'] = merged['y'].astype(int)
merged = merged[['x', 'y', 'label']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)