import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on name = hero_names
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Map Publisher strings to integer IDs starting from 1
publishers = df_joined['Publisher'].dropna().unique()
publisher_map = {name: idx+1 for idx, name in enumerate(sorted(publishers))}

# Map Publisher column to integer IDs
df_joined['Publisher'] = df_joined['Publisher'].map(publisher_map)

# Group by Publisher to get unique publisher IDs
df_result = df_joined[['Publisher']].drop_duplicates().reset_index(drop=True)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)