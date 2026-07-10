import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

# Join ratings with users on user_id to get age
ratings_users = pd.merge(src2, src1[['user_id', 'age']], how='inner', on='user_id')

# Join the above with movies on movie_id to get title and video_release_date
joined = pd.merge(ratings_users, src0[['movie_id', 'title', 'video_release_date']], how='inner', on='movie_id')

# Group by title, movie_id, user_id and aggregate rating, unix_timestamp, age by mean
agg = joined.groupby(['title', 'movie_id', 'user_id'], as_index=False).agg({
    'rating': 'mean',
    'unix_timestamp': 'mean',
    'age': 'mean',
    'video_release_date': 'first'  # video_release_date is preserved as is (no aggregation)
})

# Reorder columns to match target schema
result = agg[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)