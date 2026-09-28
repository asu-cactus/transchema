import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

union_1_2 = pd.merge(source1, source2[['user_id', 'age']], on='user_id', how='left')

merged = pd.merge(union_1_2, source0[['movie_id', 'title', 'video_release_date']], on='movie_id', how='left')

result = merged[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

result['title'] = result['title'].astype(str)
result['movie_id'] = pd.to_numeric(result['movie_id'], errors='coerce').astype('Int64')
result['video_release_date'] = pd.to_numeric(result['video_release_date'], errors='coerce')
result['user_id'] = pd.to_numeric(result['user_id'], errors='coerce')
result['rating'] = pd.to_numeric(result['rating'], errors='coerce')
result['unix_timestamp'] = pd.to_numeric(result['unix_timestamp'], errors='coerce')
result['age'] = pd.to_numeric(result['age'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)