import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

grouped = source1.groupby('movie_id').agg({
    'user_id': 'mean',
    'rating': 'mean',
    'unix_timestamp': 'mean'
}).reset_index()

join1 = pd.merge(grouped, source0, how='inner', on='movie_id')

join2 = pd.merge(join1, source1, how='inner', on=['movie_id', 'user_id', 'rating', 'unix_timestamp'])

final = pd.merge(join2, source2[['user_id', 'age']], how='inner', on='user_id')

final = final[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

final['video_release_date'] = pd.to_numeric(final['video_release_date'], errors='coerce')
final['user_id'] = final['user_id'].astype(float)
final['rating'] = final['rating'].astype(float)
final['unix_timestamp'] = final['unix_timestamp'].astype(float)
final['age'] = final['age'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)