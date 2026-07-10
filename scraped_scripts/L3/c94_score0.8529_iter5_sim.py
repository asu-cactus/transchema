import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_2.csv", index_col=0)

ratings_with_sex = source1.merge(source2[['user_id', 'sex']], on='user_id', how='inner')

avg_ratings = ratings_with_sex.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean()

pivoted = avg_ratings.pivot(index='movie_id', columns='sex', values='rating').reset_index()
pivoted.columns.name = None
pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'}).fillna(0)

result = pivoted.merge(source0[['movie_id', 'title']], on='movie_id', how='inner')

result = result[['movie_id', 'title', 'F', 'M']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_94/target_multisource_mcts.csv", index=False)