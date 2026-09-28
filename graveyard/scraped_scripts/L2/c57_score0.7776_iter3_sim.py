import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_57/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_57/training_1.csv", index_col=0)

grouped = source0.groupby('movie_id').agg(size=('movie_id', 'count'), mean=('rating', 'mean')).reset_index()

merged = pd.merge(grouped, source1, on='movie_id', how='inner')

result = merged[['title', 'size', 'mean']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_57/target_multisource_mcts.csv", index=False)