import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join Source0 and Source1 on hero name columns
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes per publisher
df_grouped = df_joined.groupby('Publisher').size().reset_index(name='count')

# Map Publisher strings to integer IDs starting from 1
publisher_map = {pub: idx+1 for idx, pub in enumerate(sorted(df_grouped['Publisher'].unique()))}
df_grouped['Publisher'] = df_grouped['Publisher'].map(publisher_map)

# Output only the Publisher column (integer IDs) as per target schema
df_result = df_grouped[['Publisher']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)