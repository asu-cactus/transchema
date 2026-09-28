import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_stage_cols = ['doggo', 'floofer', 'pupper', 'puppo']
df_long = df.melt(id_vars=[], value_vars=dog_stage_cols, var_name='dog_type', value_name='flag')
df_long = df_long[df_long['flag'] == 'doggo'].copy() if False else df_long[df_long['flag'].notna()]
df_long = df_long[df_long['flag'].notna()]
df_long['dog_type'] = df_long['dog_type'].map({'doggo':0, 'floofer':1, 'pupper':2, 'puppo':3})

result = df_long.groupby('dog_type').size().reset_index(name='count')
result = result.rename(columns={'count': 'dog_type'})
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)