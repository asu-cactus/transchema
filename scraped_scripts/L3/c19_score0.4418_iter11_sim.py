import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

union_result = pd.concat([source1, source1], ignore_index=True)

join_result_1 = pd.merge(union_result, source0[['movie_id', 'title']], on='movie_id', how='inner')

final_join = pd.merge(join_result_1, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

final = final_join[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final['user_id'] = final['user_id'].astype(float)
final['movie_id'] = final['movie_id'].astype(int)
final['rating'] = final['rating'].astype(float)
final['timestamp'] = final['timestamp'].astype(float)
final['age'] = final['age'].astype(float)
final['occupation'] = final['occupation'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)