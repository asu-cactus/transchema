import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

label_map = {v: i for i, v in enumerate(sorted(df['label'].unique()), 1)}
df['label'] = df['label'].map(label_map)

df['y'] = df['y'].astype(float)
df['x'] = df['x'].astype(int)
df['label'] = df['label'].astype(int)

df = df[['y', 'x', 'label']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)