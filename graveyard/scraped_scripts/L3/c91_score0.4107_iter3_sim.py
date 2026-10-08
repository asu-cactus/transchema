import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

union_result = pd.concat([source1, source1], ignore_index=True)

join_result_1 = pd.merge(union_result, source0[['movie_id', 'title', 'video_release_date']], on='movie_id', how='inner')

join_result_2 = pd.merge(join_result_1, source2[['user_id', 'age']], on='user_id', how='inner')

target = join_result_2[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)