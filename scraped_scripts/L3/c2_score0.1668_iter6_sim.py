import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

source0_renamed = source0.rename(columns={"user_id": "user_id", "movie_id": "movie_id", "rating": "rating", "timestamp": "timestamp"})
source2_renamed = source2.rename(columns={"user_id": "user_id", "age": "age", "occupation": "occupation"})

union_result = pd.concat([source0_renamed, source2_renamed], axis=0, ignore_index=True, sort=False)

merged = pd.merge(union_result, source1[['movie_id', 'title']], on='movie_id', how='inner')

result = merged[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

result['user_id'] = pd.to_numeric(result['user_id'], errors='coerce')
result['age'] = pd.to_numeric(result['age'], errors='coerce')
result['occupation'] = pd.to_numeric(result['occupation'], errors='coerce')
result['movie_id'] = pd.to_numeric(result['movie_id'], errors='coerce', downcast='integer')
result['rating'] = pd.to_numeric(result['rating'], errors='coerce')
result['timestamp'] = pd.to_numeric(result['timestamp'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)