import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df_long = pd.melt(df, id_vars=['tweet_id'], value_vars=['doggo', 'floofer', 'pupper', 'puppo'], var_name='dog_type', value_name='flag')
df_filtered = df_long[df_long['flag'] == 'doggo']
df_filtered = df_long[df_long['flag'].notna()]

counts = df_filtered.groupby('dog_type').agg(dog_type_count=('tweet_id', 'count')).reset_index()

mapping = {'doggo': 0, 'floofer': 1, 'pupper': 2, 'puppo': 3}
counts['dog_type'] = counts['dog_type'].map(mapping)

result = counts[['dog_type', 'dog_type_count']].rename(columns={'dog_type_count': 'dog_type'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)