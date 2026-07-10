import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

df = df0[['Batsman on strike', 'overs', 'runs scored', 'extras']].copy()
df['Batsman on strike'] = df['Batsman on strike'].astype(str)
df['overs'] = df['overs'].astype(float)
df['runs scored'] = df['runs scored'].astype(int)
df['extras'] = df['extras'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)