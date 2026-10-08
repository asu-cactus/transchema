import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

df_grouped = df0.groupby('Batsman on strike').agg({
    'overs': 'sum',
    'runs scored': 'sum',
    'extras': 'sum'
}).reset_index()

df_grouped['overs'] = df_grouped['overs'].astype(float)
df_grouped['runs scored'] = df_grouped['runs scored'].astype(int)
df_grouped['extras'] = df_grouped['extras'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)