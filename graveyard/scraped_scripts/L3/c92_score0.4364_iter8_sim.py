import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

union_1_2 = pd.merge(source2, source1[['user_id', 'age']], on='user_id', how='left')

merged = pd.merge(union_1_2, source0[['movie_id', 'title', 'video_release_date']], on='movie_id', how='left')

result = merged[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)