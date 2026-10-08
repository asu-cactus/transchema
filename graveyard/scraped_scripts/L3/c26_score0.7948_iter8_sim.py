import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)

agg = source0.groupby('movie_id').agg(
    MEAN_rating=('rating', 'mean'),
    COUNT_rating=('rating', 'count'),
    MIN_rating=('rating', 'min'),
    MAX_rating=('rating', 'max')
).reset_index()

merged = pd.merge(source1, agg, how='left', left_on='movie_id', right_on='movie_id')

result = merged[['title', 'MEAN_rating']].rename(columns={'MEAN_rating': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)