import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
df_proj = df[['year', 'movie_id']]
pivot_df = df_proj.groupby('year')['movie_id'].count().reset_index()
pivot_df.columns = ['year', '0']
pivot_df['year'] = pivot_df['year'].astype(int)
pivot_df['0'] = pivot_df['0'].astype(int)
pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)