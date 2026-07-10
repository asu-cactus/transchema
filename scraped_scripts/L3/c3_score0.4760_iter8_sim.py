import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

agg = source2.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean'
})

joined_0_2 = pd.merge(agg, source0, how='inner', on='user_id')
final = pd.merge(joined_0_2, source1[['movie_id', 'title']], how='inner', on='movie_id')

final = final[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)