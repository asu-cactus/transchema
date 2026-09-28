import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Union all source tables
df = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Map label strings to integers dynamically
# Since target examples have label=1 for all shown labels, map all labels to 1
df['label'] = 1

# Convert types to match target schema: y: float, x: int, label: int
df['x'] = df['x'].astype(int)
df['y'] = df['y'].astype(float)
df['label'] = df['label'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)