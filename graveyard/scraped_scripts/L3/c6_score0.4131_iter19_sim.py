import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_2.csv", index_col=0)

df = source0.merge(source2, on='user id').merge(source1[['movie id', 'movie title']], on='movie id')
result = df[['movie title', 'rating']].copy()
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_6/target_multisource_mcts.csv", index=False)