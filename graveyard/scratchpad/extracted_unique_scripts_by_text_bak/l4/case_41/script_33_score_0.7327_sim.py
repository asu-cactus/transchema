import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df0['label'] = df0['label'].astype(str)
df1['label'] = df1['label'].astype(str)
df2['label'] = df2['label'].astype(str)
df3['label'] = df3['label'].astype(str)

count0 = df0.groupby('label')['x'].nunique().reset_index(name='count0')
count1 = df1.groupby('label')['x'].nunique().reset_index(name='count1')
count2 = df2.groupby('label')['x'].nunique().reset_index(name='count2')
count3 = df3.groupby('label')['x'].nunique().reset_index(name='count3')

merged = count0.merge(count1, on='label', how='outer')
merged = merged.merge(count2, on='label', how='outer')
merged = merged.merge(count3, on='label', how='outer')

merged = merged.fillna(0)

merged['y'] = merged['count0'] + merged['count1'] + merged['count2'] + merged['count3']
merged['x'] = 1
merged['label'] = pd.factorize(merged['label'])[0] + 1

result = merged[['y', 'x', 'label']].copy()
result['y'] = result['y'].astype(float)
result['x'] = result['x'].astype(int)
result['label'] = result['label'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)