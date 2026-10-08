import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

s0 = s0.rename(columns={'x': 'x_0', 'y': 'y', 'label': 'label_0'})
s1 = s1.rename(columns={'x': 'x_1', 'y': 'y', 'label': 'label_1'})
s2 = s2.rename(columns={'x': 'x_2', 'y': 'y', 'label': 'label_2'})
s3 = s3.rename(columns={'x': 'x_3', 'y': 'y', 'label': 'label_3'})

df = s0.merge(s1, on='y').merge(s2, on='y').merge(s3, on='y')

df['x'] = df[['x_0', 'x_1', 'x_2', 'x_3']].min(axis=1).astype(int)

def label_to_int(label):
    if pd.isna(label):
        return 0
    if isinstance(label, str):
        return sum(ord(c) for c in label) % 1000
    return int(label)

df['label'] = df[['label_0', 'label_1', 'label_2', 'label_3']].apply(
    lambda row: next((label_to_int(v) for v in row if pd.notna(v)), 0), axis=1
).astype(int)

result = df[['y', 'x', 'label']].copy()
result['y'] = result['y'].astype(float)
result['x'] = result['x'].astype(int)
result['label'] = result['label'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)