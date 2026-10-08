import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_2.csv", index_col=0)

agg = source1.groupby(['user_id', 'movie_id'], as_index=False).agg({'rating':'mean', 'timestamp':'mean'})

merged_0_agg = pd.merge(source0, agg, on='user_id', how='inner')

final = pd.merge(merged_0_agg, source2[['movie_id', 'title']], on='movie_id', how='inner')

result = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_25/target_multisource_mcts.csv", index=False)