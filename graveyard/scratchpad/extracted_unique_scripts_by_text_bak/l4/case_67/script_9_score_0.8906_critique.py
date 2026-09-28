import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

# Group by 'Batsman on strike' and aggregate sums of overs, runs scored, and extras
df_agg = df0.groupby('Batsman on strike', as_index=False).agg({
    'overs': 'sum',
    'runs scored': 'sum',
    'extras': 'sum'
})

# Ensure correct dtypes
df_agg['overs'] = df_agg['overs'].astype(float)
df_agg['runs scored'] = df_agg['runs scored'].astype(int)
df_agg['extras'] = df_agg['extras'].astype(int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)