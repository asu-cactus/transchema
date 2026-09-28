import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_1.csv", index_col=0)

agg = source1.groupby(['movie_id', 'user_id']).rating.nunique().reset_index(name='rating')

joined = pd.merge(source0, agg, left_on='movie id', right_on='movie_id', how='inner')

result = joined.rename(columns={
    'movie title': 'movie title',
    'movie id': 'movie id',
    'user_id': 'user_id',
    'movie_id': 'movie_id',
    'rating': 'rating'
})[['movie title', 'movie id', 'user_id', 'movie_id', 'rating']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_29/target_multisource_mcts.csv", index=False)