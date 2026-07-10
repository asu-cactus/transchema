import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name
df_merged = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes
result = df_merged.groupby('Publisher', as_index=False).agg({'name': 'count'})

# Rename count column to 'Publisher' to match target schema (single integer column)
result = result.rename(columns={'name': 'Publisher'})

# Convert Publisher column to int if not already
result['Publisher'] = result['Publisher'].astype(int)

# Sort by Publisher ascending (optional, for consistent output)
result = result.sort_values('Publisher').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)