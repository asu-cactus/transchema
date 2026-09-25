import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df_proj = df[['year', 'movie_id']].copy()
df_grouped = df_proj.groupby('year', as_index=False).agg({'movie_id': 'count'})
df_grouped.rename(columns={'movie_id': '0'}, inplace=True)
df_grouped['year'] = df_grouped['year'].astype(int)
df_grouped['0'] = df_grouped['0'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)