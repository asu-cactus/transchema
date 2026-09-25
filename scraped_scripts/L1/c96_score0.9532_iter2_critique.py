import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Strip whitespace in Publisher to ensure clean join keys
df0['Publisher'] = df0['Publisher'].astype(str).str.strip()

# Join on hero name columns
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes per publisher
publisher_counts = df_joined.groupby('Publisher').size().reset_index(name='count')

# Map Publisher strings to integers
publisher_to_int = {pub: i+1 for i, pub in enumerate(sorted(publisher_counts['Publisher']))}
publisher_counts['Publisher'] = publisher_counts['Publisher'].map(publisher_to_int)

# The target schema is a single integer column 'Publisher' with counts as values
# So output the counts as 'Publisher' column
output_df = publisher_counts[['count']].rename(columns={'count': 'Publisher'})

output_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)