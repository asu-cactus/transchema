import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

agg = src2.groupby('movie_id').agg(
    user_id_count=('user_id', 'count'),
    rating_avg=('rating', 'mean'),
    timestamp_min=('timestamp', 'min'),
    timestamp_max=('timestamp', 'max')
).reset_index()

joined_1 = pd.merge(src1, src2, on='movie_id', how='inner')

joined_2 = pd.merge(joined_1, src0, on='user_id', how='inner')

result = joined_2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)