import pandas as pd

def label_to_int(label):
    if pd.isna(label):
        return 0
    if isinstance(label, str):
        return sum(ord(c) for c in label) % 1000
    return int(label)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df = pd.concat([s0, s1, s2, s3], ignore_index=True)

df['x'] = df['x'].astype(int)
df['y'] = df['y'].astype(float)
df['label'] = df['label'].apply(label_to_int).astype(int)

result = df[['y', 'x', 'label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)