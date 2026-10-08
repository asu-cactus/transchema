import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

count0 = df0.groupby('label')['x'].count().reset_index(name='count0')
count1 = df1.groupby('label')['x'].count().reset_index(name='count1')
count2 = df2.groupby('label')['x'].count().reset_index(name='count2')
count3 = df3.groupby('label')['x'].count().reset_index(name='count3')

merged = count0.merge(count1, on='label', how='outer')
merged = merged.merge(count2, on='label', how='outer')
merged = merged.merge(count3, on='label', how='outer')

merged = merged.fillna(0)

merged['x'] = (merged['count0'] + merged['count1'] + merged['count2'] + merged['count3']).astype(int)

label_map = {label: idx+1 for idx, label in enumerate(sorted(merged['label'].unique()))}
merged['label'] = merged['label'].map(label_map).astype(int)

merged['y'] = merged['x'].astype(float)

result = merged[['y', 'x', 'label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)