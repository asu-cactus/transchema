import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df = df.dropna(subset=['TransTo'])

df['TransTo'] = df['TransTo'].astype(int)
df['WarNum'] = df['WarNum'].astype(int)

df = df[['TransTo', 'WarNum']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)