import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

grouped = df0.groupby(['Batsman on strike', 'overs'], as_index=False).agg({'runs scored':'min', 'extras':'min'})

grouped['Batsman on strike'] = grouped['Batsman on strike'].astype(str)
grouped['overs'] = grouped['overs'].astype(float)
grouped['runs scored'] = grouped['runs scored'].astype(int)
grouped['extras'] = grouped['extras'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)