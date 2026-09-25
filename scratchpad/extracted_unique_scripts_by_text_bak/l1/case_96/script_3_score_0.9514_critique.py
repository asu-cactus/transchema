import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name columns
merged = pd.merge(df0[['name', 'Publisher']], df1[['hero_names']], left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count heroes
result = merged.groupby('Publisher', as_index=False).agg({'name': 'count'})

# Rename count column to 'Publisher' to match target schema
result.rename(columns={'name': 'Publisher'}, inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)