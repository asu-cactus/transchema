import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

union_result = pd.concat([source1, source1], ignore_index=True)

join_result_1 = pd.merge(union_result, source0[['movie_id', 'title']], on='movie_id', how='left')

final_df = pd.merge(join_result_1, source2[['user_id', 'age', 'occupation']], on='user_id', how='left')

final_df = final_df[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final_df['user_id'] = final_df['user_id'].astype(float)
final_df['movie_id'] = final_df['movie_id'].astype(int)
final_df['rating'] = final_df['rating'].astype(float)
final_df['timestamp'] = final_df['timestamp'].astype(float)
final_df['age'] = final_df['age'].astype(float)
final_df['occupation'] = final_df['occupation'].astype(float)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)