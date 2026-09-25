import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df0 = df0[(df0['year'] > 0) & (df0['year'].notnull()) & (df0['status'] == 'Released')]
pivot = df0.groupby('year')['movie_id'].nunique().reset_index(name='0')
pivot['year'] = pivot['year'].astype(int)
pivot['0'] = pivot['0'].astype(int)
pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)