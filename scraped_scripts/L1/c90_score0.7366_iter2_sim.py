import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

df0['dog_type'] = None
for col in ['doggo', 'floofer', 'pupper', 'puppo']:
    df0.loc[df0[col] == col, 'dog_type'] = col
df0['dog_type'] = df0['dog_type'].fillna('0')

mapping = {'doggo': 1, 'floofer': 3, 'pupper': 4, 'puppo': 5, '0': 0}
df0['dog_type'] = df0['dog_type'].map(mapping).astype(int)

result = df0.groupby('dog_type').size().reset_index(name='count')

result = result.rename(columns={'count': 'dog_type'})
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)