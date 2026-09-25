import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

# Melt dog type columns into long format
df_long = pd.melt(df, id_vars=['tweet_id'], value_vars=['doggo', 'floofer', 'pupper', 'puppo'],
                  var_name='dog_type', value_name='flag')

# Keep only rows where flag is not null (dog type applies)
df_filtered = df_long[df_long['flag'].notna()]

# Group by dog_type and count tweet_id
counts = df_filtered.groupby('dog_type').agg(dog_type=('tweet_id', 'count')).reset_index()

# Map dog_type strings to integers as per mapping
mapping = {'doggo': 0, 'floofer': 1, 'pupper': 2, 'puppo': 3}
counts['dog_type'] = counts['dog_type'].map(mapping)

# Select columns to match target schema
result = counts[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)