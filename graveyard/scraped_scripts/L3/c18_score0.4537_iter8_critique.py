import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
joined_1 = pd.merge(src2, src1, on='movie_id', how='inner')

# Join the above with users on user_id
joined_2 = pd.merge(joined_1, src0, on='user_id', how='inner')

# Select and reorder columns as per target schema
result = joined_2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Cast user_id to float to match target schema (user_id is float in target)
result['user_id'] = result['user_id'].astype(float)

# movie_id is already int, rating, timestamp, age, occupation are float-compatible

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)