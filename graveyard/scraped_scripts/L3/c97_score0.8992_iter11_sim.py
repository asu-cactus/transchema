import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

agg_min = source2.groupby('movie id')['rating'].min().reset_index(name='min_rating')
agg_max = source2.groupby('movie id')['rating'].max().reset_index(name='max_rating')
agg = pd.merge(agg_min, agg_max, on='movie id')
agg['avg_min_max_rating'] = agg[['min_rating', 'max_rating']].mean(axis=1)

merged = pd.merge(source0[['movie id', 'movie title']], agg[['movie id', 'avg_min_max_rating']], on='movie id', how='inner')

result = merged.groupby('movie title')['avg_min_max_rating'].mean().reset_index()
result = result.rename(columns={'avg_min_max_rating': 'rating'})
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)