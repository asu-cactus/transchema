import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

df0_unpivot = df0.copy()
df0_unpivot = df0_unpivot.assign(genres=df0_unpivot['genres'].str.split('|'))
df0_unpivot = df0_unpivot.explode('genres').rename(columns={'genres':'genre'})

joined_01 = pd.merge(df0_unpivot, df1, on='movie_id', how='inner')
joined_all = pd.merge(joined_01, df2, on='user_id', how='inner')

result = joined_all[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)