import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_1.csv", index_col=0)

agg = source1.groupby(['user_id', 'movie_id']).agg(
    rating_count=('rating', 'count'),
    rating_avg=('rating', 'mean'),
    rating_min=('rating', 'min'),
    rating_max=('rating', 'max')
).reset_index()

joined = pd.merge(agg, source0, left_on='movie_id', right_on='movie id', how='inner')

joined['movie title'] = joined['movie title'].astype(str)
joined['movie id'] = joined['movie id'].astype(int)
joined['user_id'] = joined['user_id'].astype(int)
joined['movie_id'] = joined['movie_id'].astype(int)

joined['rating'] = joined['rating_max'].round().astype(int)

result = joined[['movie title', 'movie id', 'user_id', 'movie_id', 'rating']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_29/target_multisource_mcts.csv", index=False)