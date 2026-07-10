import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

df_unpivot = df0[['year', 'vote_count']].copy()
df_unpivot.columns = ['year', '0']

df_grouped = df_unpivot.groupby('year', as_index=False).sum()
df_grouped['year'] = df_grouped['year'].astype(int)
df_grouped['0'] = df_grouped['0'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)