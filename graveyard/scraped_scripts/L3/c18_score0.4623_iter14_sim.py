import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

agg = src2.groupby(['user_id', 'movie_id']).agg(
    rating=('rating', 'mean'),
    timestamp_min=('timestamp', 'min'),
    timestamp_max=('timestamp', 'max')
).reset_index()

agg['timestamp'] = (agg['timestamp_min'] + agg['timestamp_max']) / 2
agg = agg.drop(columns=['timestamp_min', 'timestamp_max'])

join1 = pd.merge(agg, src0, how='inner', on='user_id')
join2 = pd.merge(join1, src1[['movie_id', 'title']], how='inner', on='movie_id')

result = join2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)