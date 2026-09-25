import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df_filtered = df[df['year'].notnull() & (df['year'] > 0)]
result = df_filtered.groupby('year', as_index=False).agg({'movie_id': 'count'})
result.rename(columns={'movie_id': '0'}, inplace=True)
result['year'] = result['year'].astype(int)
result['0'] = result['0'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)