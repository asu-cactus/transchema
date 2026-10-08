import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df0 = df0[(df0['year'].notnull()) & (df0['year'] > 0) & (df0['status'] == 'Released')]

pivot_df = df0.groupby('year').size().reset_index(name='0')
pivot_df['year'] = pivot_df['year'].astype(int)
pivot_df['0'] = pivot_df['0'].astype(int)

pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)