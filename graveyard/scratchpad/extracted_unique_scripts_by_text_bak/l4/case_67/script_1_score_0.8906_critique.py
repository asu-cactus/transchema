import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

# Select relevant columns
df = df0[['Batsman on strike', 'overs', 'runs scored', 'extras']].copy()

# Convert types as per target schema
df['Batsman on strike'] = df['Batsman on strike'].astype(str)
df['overs'] = df['overs'].astype(float)
df['runs scored'] = df['runs scored'].astype(int)
df['extras'] = df['extras'].astype(int)

# Group by 'Batsman on strike' and aggregate sums of overs, runs scored, extras
df_grouped = df.groupby('Batsman on strike', as_index=False).agg({
    'overs': 'sum',
    'runs scored': 'sum',
    'extras': 'sum'
})

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)