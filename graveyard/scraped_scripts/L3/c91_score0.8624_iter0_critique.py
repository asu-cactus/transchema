import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

# Join ratings with user info on user_id
join1 = pd.merge(source1, source2, how='inner', on='user_id')

# Join the above with movie info on movie_id
join2 = pd.merge(join1, source0, how='inner', on='movie_id')

# Group by title and movie_id, aggregate other columns by mean
final = join2.groupby(['title', 'movie_id'], as_index=False).agg({
    'video_release_date': 'mean',
    'user_id': 'mean',
    'rating': 'mean',
    'unix_timestamp': 'mean',
    'age': 'mean'
})

# Ensure correct dtypes as per target schema
final['video_release_date'] = pd.to_numeric(final['video_release_date'], errors='coerce')
final['user_id'] = final['user_id'].astype(float)
final['rating'] = final['rating'].astype(float)
final['unix_timestamp'] = final['unix_timestamp'].astype(float)
final['age'] = final['age'].astype(float)

final = final[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)