import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv', index_col=0)

# If there were multiple source tables, we would read and concat them all here.
# Since only one source is given, just use df0.
df = pd.concat([df0], ignore_index=True)

df['condition'] = df['condition'].astype(int)
df['click'] = df['click'].astype(float)

# Group by 'condition' and aggregate mean of 'click'
df = df.groupby('condition', as_index=False).agg({'click': 'mean'})

df.to_csv('autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv', index=False)