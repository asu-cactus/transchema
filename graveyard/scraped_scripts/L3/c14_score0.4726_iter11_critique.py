import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

# Join Source1 and Source0 on movie_id
merged_0 = pd.merge(source1, source0, on='movie_id', how='inner')

# Join the above with Source2 on user_id
merged_1 = pd.merge(merged_0, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Select columns in target schema order
result = merged_1[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)