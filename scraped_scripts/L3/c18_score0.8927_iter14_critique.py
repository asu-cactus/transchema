import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

# Join source2 (ratings) with source0 (user info) on user_id
joined = pd.merge(src2, src0, how='inner', on='user_id')

# Group by movie_id, aggregate averages of user_id, rating, timestamp, age, occupation
agg = joined.groupby('movie_id').agg(
    user_id=('user_id', 'mean'),
    rating=('rating', 'mean'),
    timestamp=('timestamp', 'mean'),
    age=('age', 'mean'),
    occupation=('occupation', 'mean')
).reset_index()

# Join aggregated data with source1 (movie info) on movie_id to get title
result = pd.merge(agg, src1[['movie_id', 'title']], how='inner', on='movie_id')

# Reorder columns to match target schema
result = result[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)