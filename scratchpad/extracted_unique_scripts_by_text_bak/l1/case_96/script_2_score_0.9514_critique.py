import pandas as pd

# Read source tables
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv', index_col=0)

# Join on hero name
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes per publisher
df_grouped = df_joined.groupby('Publisher').size().reset_index(name='count')

# Map Publisher strings to integer IDs
publisher_ids, uniques = pd.factorize(df_grouped['Publisher'])

# Create final DataFrame with Publisher as integer (the count)
# The target schema is ['Publisher': integer], and examples look like counts
# So output the counts as Publisher column (integer)
result = pd.DataFrame({'Publisher': df_grouped['count'].astype(int)})

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv', index=False)