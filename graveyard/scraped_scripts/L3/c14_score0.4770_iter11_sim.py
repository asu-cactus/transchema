import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

agg = source1.groupby(['movie_id', 'user_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean'
})

merged_0 = pd.merge(source0, agg, on='movie_id', how='inner')
merged_1 = pd.merge(merged_0, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

result = merged_1[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)