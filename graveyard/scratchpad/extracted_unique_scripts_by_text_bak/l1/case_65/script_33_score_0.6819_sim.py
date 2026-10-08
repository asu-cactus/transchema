import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df_proj = df0[['year', 'vote_count']]
df_grouped = df_proj.groupby('year', as_index=False).sum()
df_grouped.rename(columns={'vote_count': '0'}, inplace=True)
df_grouped['year'] = df_grouped['year'].astype(int)
df_grouped['0'] = df_grouped['0'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)