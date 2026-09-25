import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Map labels to integers consistently across all sources
all_labels = pd.concat([df0['label'], df1['label'], df2['label'], df3['label']])
label_map = {label: idx+1 for idx, label in enumerate(sorted(all_labels.unique()))}

df0['label'] = df0['label'].map(label_map)
df1['label'] = df1['label'].map(label_map)
df2['label'] = df2['label'].map(label_map)
df3['label'] = df3['label'].map(label_map)

# Group by label in each source and aggregate y by mean, count x in df0
agg0 = df0.groupby('label').agg(y0=('y', 'mean'), x_count=('x', 'count')).reset_index()
agg1 = df1.groupby('label').agg(y1=('y', 'mean')).reset_index()
agg2 = df2.groupby('label').agg(y2=('y', 'mean')).reset_index()
agg3 = df3.groupby('label').agg(y3=('y', 'mean')).reset_index()

# Merge all aggregated results on label
merged = agg0.merge(agg1, on='label', how='outer')
merged = merged.merge(agg2, on='label', how='outer')
merged = merged.merge(agg3, on='label', how='outer')

# Compute average y across all sources per label
merged['y'] = merged[['y0','y1','y2','y3']].mean(axis=1)

# x is count of x in df0 grouped by label
merged['x'] = merged['x_count']

# Final target columns: y (float), x (int), label (int)
result = merged[['y','x','label']].copy()
result['x'] = result['x'].fillna(0).astype(int)
result['y'] = result['y'].astype(float)
result['label'] = result['label'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)