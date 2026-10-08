import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df0.groupby(['userId', 'movieId']).agg(
    rating=('rating', 'mean')
).reset_index()

joined = pd.merge(agg, df1, on='movieId', how='inner')

joined['userId'] = joined['userId'].astype(float)
joined['movieId'] = joined['movieId'].astype(int)
joined['title'] = joined['title'].astype(str)
joined['genres'] = joined['genres'].astype(str)
joined['rating'] = joined['rating'].astype(float)

result = joined[['movieId', 'title', 'genres', 'userId', 'rating']]

result.to_csv(target_path, index=False)