import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

agg = source1.groupby(['movie_id', 'user_id'], as_index=False).agg({
    'rating': 'mean',
    'unix_timestamp': 'mean'
})

agg = agg.merge(source2[['user_id', 'age']], on='user_id', how='left')
agg['age'] = agg.groupby('user_id')['age'].transform('mean')

result = agg.merge(source0[['movie_id', 'title', 'video_release_date']], on='movie_id', how='inner')

result = result[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)