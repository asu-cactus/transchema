import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Convert label columns to consistent integer codes across all sources
all_labels = pd.concat([s0['label'], s1['label'], s2['label'], s3['label']])
label_codes = pd.Series(all_labels.unique()).reset_index(drop=True)
label_map = {v: i+1 for i, v in enumerate(label_codes)}

s0['label'] = s0['label'].map(label_map)
s1['label'] = s1['label'].map(label_map)
s2['label'] = s2['label'].map(label_map)
s3['label'] = s3['label'].map(label_map)

# Group by label in each source, aggregate min x and count y
g0 = s0.groupby('label').agg(x0_min=('x', 'min'), y0_count=('y', 'count')).reset_index()
g1 = s1.groupby('label').agg(x1_min=('x', 'min')).reset_index()
g2 = s2.groupby('label').agg(x2_min=('x', 'min')).reset_index()
g3 = s3.groupby('label').agg(x3_min=('x', 'min')).reset_index()

# Merge all grouped results on label
df = g0.merge(g1, on='label', how='outer')
df = df.merge(g2, on='label', how='outer')
df = df.merge(g3, on='label', how='outer')

# For each label, take the minimum x among the four min x columns
df['x'] = df[['x0_min', 'x1_min', 'x2_min', 'x3_min']].min(axis=1)

# y is the count of y from Source0 grouped by label, convert to float
df['y'] = df['y0_count'].astype(float)

# label is already integer
df = df[['y', 'x', 'label']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)