import pandas as pd

# Read all source tables
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_24/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_24/training_2.csv', index_col=0)

# Select relevant columns and ensure correct types
df0 = df0[['condition', 'click']].astype({'condition': int, 'click': int})
df1 = df1[['condition', 'click']].astype({'condition': int, 'click': int})
df2 = df2[['condition', 'click']].astype({'condition': int, 'click': int})

# UNION all source tables
df = pd.concat([df0, df1, df2], ignore_index=True)

# GROUP BY 'condition' and aggregate sum of 'click'
df = df.groupby('condition', as_index=False).agg({'click': 'sum'})

# Write output
df.to_csv('autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv', index=False)