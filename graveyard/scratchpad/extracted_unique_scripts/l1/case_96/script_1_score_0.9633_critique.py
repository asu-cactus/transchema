import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Strip whitespace from 'Publisher' to ensure clean join keys
df0['Publisher'] = df0['Publisher'].astype(str).str.strip()

# Join on hero names: df0.name and df1.hero_names
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes per publisher
publisher_counts = df_joined.groupby('Publisher').size().reset_index(name='count')

# Factorize Publisher to integer IDs starting from 1
publisher_counts['Publisher'] = pd.factorize(publisher_counts['Publisher'])[0] + 1

# Rename count column to 'Publisher' to match target schema
publisher_counts.rename(columns={'count': 'Publisher'}, inplace=True)

# Keep only the 'Publisher' column (integer counts)
output_df = publisher_counts[['Publisher']]

output_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)