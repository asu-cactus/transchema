import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Union all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Map label to integer codes
label_map = {label: idx + 1 for idx, label in enumerate(sorted(df['label'].unique()))}
df['label'] = df['label'].map(label_map).astype(int)

# Convert x to integer (by truncation)
df['x'] = df['x'].astype(int)

# y remains float
df['y'] = df['y'].astype(float)

# Select columns in target schema order
result = df[['y', 'x', 'label']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)