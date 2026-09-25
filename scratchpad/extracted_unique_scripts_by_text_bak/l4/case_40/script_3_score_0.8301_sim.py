import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

label_map = {v: i for i, v in enumerate(sorted(df['label'].unique()))}
df['label'] = df['label'].map(label_map)
df['y'] = df['y'].astype(int)
df['x'] = df['x'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)