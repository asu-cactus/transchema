import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes per publisher
result = df_joined.groupby('Publisher', as_index=False).agg({'name': 'count'})

# Rename count column to 'Publisher' to match target schema
result.rename(columns={'name': 'Publisher'}, inplace=True)

# The target 'Publisher' column is integer, ensure dtype is int
result['Publisher'] = result['Publisher'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)