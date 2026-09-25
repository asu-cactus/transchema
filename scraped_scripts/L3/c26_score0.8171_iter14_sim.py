import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_2.csv", index_col=0)

agg = source0.groupby('movie_id').agg(
    count_rating=('rating', 'count'),
    avg_rating=('rating', 'mean'),
    min_rating=('rating', 'min'),
    max_rating=('rating', 'max')
).reset_index()

merged = pd.merge(source1, agg, how='inner', left_on='movie_id', right_on='movie_id')

merged['0'] = (merged['count_rating'] - merged['max_rating']) / merged['count_rating']
result = merged[['title', '0']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)