import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

# Join Source0 (ratings) with Source2 (user info) on user_id
merged_user = pd.merge(source0, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Join the above with Source1 (movie info) on movie_id
merged_all = pd.merge(merged_user, source1[['movie_id', 'title']], on='movie_id', how='inner')

# Select and reorder columns as per target schema
result = merged_all[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

# Convert columns to appropriate types matching target schema
result['user_id'] = pd.to_numeric(result['user_id'], errors='coerce')
result['age'] = pd.to_numeric(result['age'], errors='coerce')
result['occupation'] = pd.to_numeric(result['occupation'], errors='coerce')
result['movie_id'] = pd.to_numeric(result['movie_id'], errors='coerce', downcast='integer')
result['rating'] = pd.to_numeric(result['rating'], errors='coerce')
result['timestamp'] = pd.to_numeric(result['timestamp'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)