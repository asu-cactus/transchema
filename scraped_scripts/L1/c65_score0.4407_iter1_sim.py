import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

df = df0[['year']].copy()
df['0'] = df0['year'].astype(int)

df = df[['year', '0']]
df['year'] = df['year'].astype(int)
df['0'] = df['0'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)