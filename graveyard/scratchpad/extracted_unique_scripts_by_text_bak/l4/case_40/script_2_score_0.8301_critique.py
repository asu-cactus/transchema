import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert 'y' and 'label' to integer type as per target schema
df['y'] = df['y'].astype(int)
df['label'] = df['label'].astype(int)

# Ensure column order matches target schema
df = df[['x', 'y', 'label']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)