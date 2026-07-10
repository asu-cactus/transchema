import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_2.csv", index_col=0)

# Join ratings with user sex
ratings_with_sex = source1.merge(source2[['user_id', 'sex']], on='user_id', how='inner')

# Group by movie_id and sex, aggregate average rating
avg_ratings = ratings_with_sex.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean()

# Pivot sex to columns F and M
pivoted = avg_ratings.pivot(index='movie_id', columns='sex', values='rating').reset_index()
pivoted.columns.name = None

# Left join movies with pivoted ratings to keep all movies
result = source0[['movie_id', 'title']].merge(pivoted, on='movie_id', how='left')

# Fill missing ratings with 0
result = result.fillna({'F': 0, 'M': 0})

# Select columns in target schema order
result = result[['movie_id', 'title', 'F', 'M']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_94/target_multisource_mcts.csv", index=False)