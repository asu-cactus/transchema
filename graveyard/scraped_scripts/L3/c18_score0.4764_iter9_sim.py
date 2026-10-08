import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

pivot_result = source2.pivot_table(index=['user_id', 'movie_id'], values=['rating', 'timestamp'], aggfunc='mean').reset_index()

join_result_1 = pd.merge(pivot_result, source1[['movie_id', 'title']], on='movie_id', how='left')

final_df = pd.merge(join_result_1, source0[['user_id', 'age', 'occupation']], on='user_id', how='left')

final_df = final_df[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)