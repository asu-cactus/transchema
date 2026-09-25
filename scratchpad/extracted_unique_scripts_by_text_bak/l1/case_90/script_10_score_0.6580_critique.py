import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df_long = df.melt(id_vars=['tweet_id'], value_vars=['doggo', 'floofer', 'pupper', 'puppo'], var_name='dog_type', value_name='flag')
df_filtered = df_long[df_long['flag'].notna()]
df_filtered['dog_type'] = df_filtered['dog_type'].map({'doggo':0, 'floofer':1, 'pupper':2, 'puppo':3})

result = df_filtered.groupby('dog_type').size().reset_index(name='dog_type')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)