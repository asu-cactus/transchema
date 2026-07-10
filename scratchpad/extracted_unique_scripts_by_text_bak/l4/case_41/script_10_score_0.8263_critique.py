import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['y'] = df['y'].astype(float)
# Convert 'x' to integer by rounding to nearest integer (to better match target)
df['x'] = df['x'].round().astype(int)

label_map = {v: i for i, v in enumerate(sorted(df['label'].unique()), 1)}
df['label'] = df['label'].map(label_map).astype(int)

df = df[['y', 'x', 'label']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)